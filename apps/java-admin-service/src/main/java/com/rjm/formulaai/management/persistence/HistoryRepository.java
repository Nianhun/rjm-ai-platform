package com.rjm.formulaai.management.persistence;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.rjm.formulaai.management.dto.AiChatRequest;
import com.rjm.formulaai.management.dto.AiChatResponse;
import com.rjm.formulaai.management.dto.FormulaRecommendationResponse;
import com.rjm.formulaai.management.dto.FormulaRequest;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import javax.sql.DataSource;

public class HistoryRepository {
    private final DataSource dataSource;
    private final ObjectMapper objectMapper;

    public HistoryRepository(DataSource dataSource, ObjectMapper objectMapper) {
        this.dataSource = dataSource;
        this.objectMapper = objectMapper;
    }

    public void recordFormula(String email, FormulaRequest request, FormulaRecommendationResponse response) {
        if (isBlank(email)) {
            return;
        }
        executeUpdate(
                "insert into formula_request_history (email, request_id, goal, dosage_form, request_json, response_json) values (?, ?, ?, ?, ?, ?)",
                email,
                request.getId(),
                request.getGoal(),
                request.getDosageForm(),
                toJson(request),
                toJson(response));
    }

    public void recordChat(String email, AiChatRequest request, AiChatResponse response) {
        if (isBlank(email)) {
            return;
        }
        executeUpdate(
                "insert into ai_chat_history (email, message, answer, request_json, response_json) values (?, ?, ?, ?, ?)",
                email,
                request.getMessage(),
                response.getAnswer(),
                toJson(request),
                toJson(response));
    }

    public List<Map<String, Object>> listFormulaHistory(String email, int limit) {
        return queryHistory(
                "select id, request_id, goal, dosage_form, request_json, response_json, created_at from formula_request_history where email = ? order by id desc limit ?",
                email,
                Math.max(1, Math.min(limit, 100)));
    }

    public List<Map<String, Object>> listChatHistory(String email, int limit) {
        return queryHistory(
                "select id, message, answer, request_json, response_json, created_at from ai_chat_history where email = ? order by id desc limit ?",
                email,
                Math.max(1, Math.min(limit, 100)));
    }

    private List<Map<String, Object>> queryHistory(String sql, String email, int limit) {
        List<Map<String, Object>> items = new ArrayList<Map<String, Object>>();
        Connection connection = null;
        PreparedStatement statement = null;
        ResultSet rows = null;
        try {
            connection = dataSource.getConnection();
            statement = connection.prepareStatement(sql);
            statement.setString(1, email);
            statement.setInt(2, limit);
            rows = statement.executeQuery();
            while (rows.next()) {
                Map<String, Object> item = new LinkedHashMap<String, Object>();
                int columnCount = rows.getMetaData().getColumnCount();
                for (int i = 1; i <= columnCount; i++) {
                    String name = rows.getMetaData().getColumnLabel(i).toLowerCase();
                    if ("request_json".equals(name) || "response_json".equals(name)) {
                        item.put(name, fromJson(rows.getString(i)));
                    } else {
                        Object value = rows.getObject(i);
                        item.put(name, value instanceof Timestamp ? value.toString() : value);
                    }
                }
                items.add(item);
            }
            return items;
        } catch (Exception exception) {
            throw new IllegalStateException("读取历史记录失败", exception);
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
            throw new IllegalStateException("写入历史记录失败", exception);
        } finally {
            closeQuietly(statement);
            closeQuietly(connection);
        }
    }

    private String toJson(Object value) {
        try {
            return objectMapper.writeValueAsString(value);
        } catch (Exception exception) {
            throw new IllegalStateException("历史记录序列化失败", exception);
        }
    }

    private Object fromJson(String value) {
        if (isBlank(value)) {
            return null;
        }
        try {
            return objectMapper.readValue(value, Object.class);
        } catch (Exception exception) {
            return value;
        }
    }

    private boolean isBlank(String value) {
        return value == null || value.trim().isEmpty();
    }

    private void closeQuietly(AutoCloseable closeable) {
        if (closeable == null) return;
        try {
            closeable.close();
        } catch (Exception ignored) {
        }
    }
}
