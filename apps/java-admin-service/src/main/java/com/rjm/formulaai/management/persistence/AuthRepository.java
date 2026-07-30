package com.rjm.formulaai.management.persistence;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import javax.sql.DataSource;

public class AuthRepository {
    private static final long EMAIL_CODE_TTL_MILLIS = 10L * 60L * 1000L;
    private static final long SESSION_TTL_MILLIS = 7L * 24L * 60L * 60L * 1000L;

    private final DataSource dataSource;
    private final SecureRandom random = new SecureRandom();
    private final String bootstrapInviteCode;

    public AuthRepository(DataSource dataSource, String bootstrapInviteCode) {
        this.dataSource = dataSource;
        this.bootstrapInviteCode = clean(bootstrapInviteCode).isEmpty() ? "RJM-BOOTSTRAP" : clean(bootstrapInviteCode);
    }

    public Map<String, Object> sendEmailCode(String email) {
        String normalizedEmail = normalizeEmail(email);
        String code = String.format("%06d", random.nextInt(1000000));
        upsertEmailCode(normalizedEmail, code, System.currentTimeMillis() + EMAIL_CODE_TTL_MILLIS);
        Map<String, Object> result = new LinkedHashMap<String, Object>();
        result.put("sent", true);
        result.put("email", normalizedEmail);
        result.put("expires_in_seconds", EMAIL_CODE_TTL_MILLIS / 1000L);
        result.put("dev_code", code);
        return result;
    }

    public Map<String, Object> register(String email, String password, String inviteCode, String verificationCode) {
        String normalizedEmail = normalizeEmail(email);
        validatePassword(password);
        validateVerificationCode(normalizedEmail, clean(verificationCode));
        ensureBootstrapInvite();
        Connection connection = null;
        try {
            connection = dataSource.getConnection();
            connection.setAutoCommit(false);
            if (userExists(connection, normalizedEmail)) {
                throw new IllegalArgumentException("该邮箱已经注册");
            }
            if (!consumeInvite(connection, inviteCode, normalizedEmail)) {
                throw new IllegalArgumentException("邀请码无效或已被使用");
            }
            PreparedStatement statement = connection.prepareStatement("insert into app_user (email, password_hash) values (?, ?)");
            try {
                statement.setString(1, normalizedEmail);
                statement.setString(2, hashPassword(password));
                statement.executeUpdate();
            } finally {
                closeQuietly(statement);
            }
            connection.commit();
            return sessionResponse(normalizedEmail);
        } catch (RuntimeException exception) {
            rollbackQuietly(connection);
            throw exception;
        } catch (Exception exception) {
            rollbackQuietly(connection);
            throw new IllegalStateException("注册失败", exception);
        } finally {
            closeQuietly(connection);
        }
    }

    public Map<String, Object> login(String email, String password) {
        String normalizedEmail = normalizeEmail(email);
        String storedHash = queryString("select password_hash from app_user where email = ?", normalizedEmail);
        if (storedHash == null || !storedHash.equals(hashPassword(password))) {
            throw new IllegalArgumentException("邮箱或密码错误");
        }
        return sessionResponse(normalizedEmail);
    }

    public Map<String, Object> me(String token) {
        String email = emailForToken(token);
        if (email == null) {
            throw new IllegalArgumentException("请登录后再访问");
        }
        Map<String, Object> result = new LinkedHashMap<String, Object>();
        result.put("authenticated", true);
        result.put("email", email);
        return result;
    }

    public void logout(String token) {
        if (!clean(token).isEmpty()) {
            executeUpdate("delete from app_session where token = ?", clean(token));
        }
    }

    public String emailForToken(String token) {
        if (clean(token).isEmpty()) {
            return null;
        }
        Connection connection = null;
        PreparedStatement statement = null;
        ResultSet rows = null;
        try {
            connection = dataSource.getConnection();
            statement = connection.prepareStatement("select email, expires_at from app_session where token = ?");
            statement.setString(1, clean(token));
            rows = statement.executeQuery();
            if (!rows.next()) {
                return null;
            }
            if (rows.getLong("expires_at") < System.currentTimeMillis()) {
                return null;
            }
            return rows.getString("email");
        } catch (Exception exception) {
            throw new IllegalStateException("会话校验失败", exception);
        } finally {
            closeQuietly(rows);
            closeQuietly(statement);
            closeQuietly(connection);
        }
    }

    public Map<String, Object> createInvite(String creatorEmail) {
        String email = normalizeEmail(creatorEmail);
        String code = "RJM-" + randomHex(8).toUpperCase();
        executeUpdate("insert into invite_code (code, created_by_email) values (?, ?)", code, email);
        Map<String, Object> result = new LinkedHashMap<String, Object>();
        result.put("code", code);
        result.put("used", false);
        return result;
    }

    public List<Map<String, Object>> listInvites(String creatorEmail) {
        String email = normalizeEmail(creatorEmail);
        List<Map<String, Object>> invites = new ArrayList<Map<String, Object>>();
        Connection connection = null;
        PreparedStatement statement = null;
        ResultSet rows = null;
        try {
            connection = dataSource.getConnection();
            statement = connection.prepareStatement(
                    "select code, used_by_email, used_at, created_at from invite_code where created_by_email = ? order by created_at desc");
            statement.setString(1, email);
            rows = statement.executeQuery();
            while (rows.next()) {
                Map<String, Object> invite = new LinkedHashMap<String, Object>();
                invite.put("code", rows.getString("code"));
                invite.put("used", rows.getString("used_by_email") != null);
                invite.put("used_by_email", rows.getString("used_by_email"));
                invite.put("used_at", stringValue(rows.getObject("used_at")));
                invite.put("created_at", stringValue(rows.getObject("created_at")));
                invites.add(invite);
            }
            return invites;
        } catch (Exception exception) {
            throw new IllegalStateException("读取邀请码失败", exception);
        } finally {
            closeQuietly(rows);
            closeQuietly(statement);
            closeQuietly(connection);
        }
    }

    private Map<String, Object> sessionResponse(String email) {
        String token = randomHex(32);
        long expiresAt = System.currentTimeMillis() + SESSION_TTL_MILLIS;
        executeUpdate("insert into app_session (token, email, expires_at) values (?, ?, ?)", token, email, expiresAt);
        Map<String, Object> result = new LinkedHashMap<String, Object>();
        result.put("token", token);
        result.put("email", email);
        result.put("expires_at", expiresAt);
        return result;
    }

    private void validateVerificationCode(String email, String code) {
        Connection connection = null;
        PreparedStatement statement = null;
        ResultSet rows = null;
        try {
            connection = dataSource.getConnection();
            statement = connection.prepareStatement("select code, expires_at from email_verification_code where email = ?");
            statement.setString(1, email);
            rows = statement.executeQuery();
            if (!rows.next()) {
                throw new IllegalArgumentException("请先获取邮箱验证码");
            }
            if (!rows.getString("code").equals(code) || rows.getLong("expires_at") < System.currentTimeMillis()) {
                throw new IllegalArgumentException("邮箱验证码错误或已过期");
            }
        } catch (RuntimeException exception) {
            throw exception;
        } catch (Exception exception) {
            throw new IllegalStateException("验证码校验失败", exception);
        } finally {
            closeQuietly(rows);
            closeQuietly(statement);
            closeQuietly(connection);
        }
    }

    private boolean consumeInvite(Connection connection, String code, String email) throws Exception {
        PreparedStatement statement = connection.prepareStatement(
                "update invite_code set used_by_email = ?, used_at = current_timestamp where code = ? and used_by_email is null");
        try {
            statement.setString(1, email);
            statement.setString(2, clean(code));
            return statement.executeUpdate() == 1;
        } finally {
            closeQuietly(statement);
        }
    }

    private boolean userExists(Connection connection, String email) throws Exception {
        PreparedStatement statement = connection.prepareStatement("select count(*) from app_user where email = ?");
        ResultSet rows = null;
        try {
            statement.setString(1, email);
            rows = statement.executeQuery();
            rows.next();
            return rows.getInt(1) > 0;
        } finally {
            closeQuietly(rows);
            closeQuietly(statement);
        }
    }

    private void ensureBootstrapInvite() {
        upsertBootstrapInvite();
    }

    private void upsertEmailCode(String email, String code, long expiresAt) {
        Connection connection = null;
        PreparedStatement statement = null;
        try {
            connection = dataSource.getConnection();
            String sql = isPostgres(connection)
                    ? "insert into email_verification_code (email, code, expires_at) values (?, ?, ?) on conflict (email) do update set code = excluded.code, expires_at = excluded.expires_at"
                    : "merge into email_verification_code (email, code, expires_at) key(email) values (?, ?, ?)";
            statement = connection.prepareStatement(sql);
            statement.setString(1, email);
            statement.setString(2, code);
            statement.setLong(3, expiresAt);
            statement.executeUpdate();
        } catch (Exception exception) {
            throw new IllegalStateException("写入验证码失败", exception);
        } finally {
            closeQuietly(statement);
            closeQuietly(connection);
        }
    }

    private void upsertBootstrapInvite() {
        Connection connection = null;
        PreparedStatement statement = null;
        try {
            connection = dataSource.getConnection();
            String sql = isPostgres(connection)
                    ? "insert into invite_code (code, created_by_email) values (?, ?) on conflict (code) do nothing"
                    : "merge into invite_code (code, created_by_email) key(code) values (?, ?)";
            statement = connection.prepareStatement(sql);
            statement.setString(1, bootstrapInviteCode);
            statement.setString(2, "system");
            statement.executeUpdate();
        } catch (Exception exception) {
            throw new IllegalStateException("初始化邀请码失败", exception);
        } finally {
            closeQuietly(statement);
            closeQuietly(connection);
        }
    }

    private boolean isPostgres(Connection connection) throws Exception {
        return connection.getMetaData().getDatabaseProductName().toLowerCase().contains("postgres");
    }

    private String normalizeEmail(String email) {
        String value = clean(email).toLowerCase();
        if (!value.matches("^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$")) {
            throw new IllegalArgumentException("账号必须使用邮箱");
        }
        return value;
    }

    private void validatePassword(String password) {
        if (password == null || password.length() < 6
                || !password.matches(".*[a-z].*")
                || !password.matches(".*[A-Z].*")
                || !password.matches(".*\\d.*")) {
            throw new IllegalArgumentException("密码至少 6 位，并且必须同时包含英文大写、小写和数字");
        }
    }

    private String hashPassword(String password) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] bytes = digest.digest(("rjm-formula-ai:" + password).getBytes(StandardCharsets.UTF_8));
            StringBuilder builder = new StringBuilder();
            for (byte item : bytes) {
                builder.append(String.format("%02x", item));
            }
            return builder.toString();
        } catch (Exception exception) {
            throw new IllegalStateException("密码处理失败", exception);
        }
    }

    private String randomHex(int bytes) {
        byte[] value = new byte[bytes];
        random.nextBytes(value);
        StringBuilder builder = new StringBuilder();
        for (byte item : value) {
            builder.append(String.format("%02x", item));
        }
        return builder.toString();
    }

    private String queryString(String sql, Object... args) {
        Connection connection = null;
        PreparedStatement statement = null;
        ResultSet rows = null;
        try {
            connection = dataSource.getConnection();
            statement = connection.prepareStatement(sql);
            for (int i = 0; i < args.length; i++) {
                statement.setObject(i + 1, args[i]);
            }
            rows = statement.executeQuery();
            return rows.next() ? rows.getString(1) : null;
        } catch (Exception exception) {
            throw new IllegalStateException("读取认证数据失败", exception);
        } finally {
            closeQuietly(rows);
            closeQuietly(statement);
            closeQuietly(connection);
        }
    }

    private void executeUpdate(String sql, Object... args) {
        Connection connection = null;
        PreparedStatement statement = null;
        try {
            connection = dataSource.getConnection();
            statement = connection.prepareStatement(sql);
            for (int i = 0; i < args.length; i++) {
                statement.setObject(i + 1, args[i]);
            }
            statement.executeUpdate();
        } catch (Exception exception) {
            throw new IllegalStateException("写入认证数据失败", exception);
        } finally {
            closeQuietly(statement);
            closeQuietly(connection);
        }
    }

    private String clean(String value) {
        return value == null ? "" : value.trim();
    }

    private String stringValue(Object value) {
        return value == null ? null : String.valueOf(value);
    }

    private void rollbackQuietly(Connection connection) {
        if (connection == null) return;
        try {
            connection.rollback();
        } catch (Exception ignored) {
        }
    }

    private void closeQuietly(AutoCloseable closeable) {
        if (closeable == null) return;
        try {
            closeable.close();
        } catch (Exception ignored) {
        }
    }
}
