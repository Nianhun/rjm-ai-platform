# RJM Formula AI 数据库部署说明

## 本地开发数据库

本地默认使用文件型 H2 数据库，不需要额外安装数据库服务。

启动 Java 管理服务后会自动创建：

```powershell
F:\zky\RJM\apps\java-admin-service\data\runtime\java-db\rjm_formula_ai.mv.db
```

默认配置位于：

```yaml
rjm:
  auth:
    enabled: true
    bootstrap-invite-code: RJM-BOOTSTRAP
  local-db:
    enabled: true
    url: jdbc:h2:file:./data/runtime/java-db/rjm_formula_ai;AUTO_SERVER=TRUE
    username: sa
    password:
    schema-path: ../../infrastructure/database/java-management/schema.h2.sql
```

本地第一次注册可使用启动邀请码：

```text
RJM-BOOTSTRAP
```

登录后进入“邀请码管理”页面，可以生成新的单次邀请码。每个邀请码只能注册一个账号。

## 云端生产数据库

云端建议使用 PostgreSQL。Java 管理服务已经提供 `cloud` profile 和 PostgreSQL schema。

### 1. 创建数据库

在云端机器或托管数据库上创建库和账号：

```sql
create database rjm_formula_ai;
create user rjm_app with encrypted password 'replace-with-strong-password';
grant all privileges on database rjm_formula_ai to rjm_app;
```

### 2. 配置环境变量

云端启动 Java 服务前设置：

```powershell
$env:SPRING_PROFILES_ACTIVE="cloud"
$env:RJM_DATABASE_URL="jdbc:postgresql://127.0.0.1:5432/rjm_formula_ai"
$env:RJM_DATABASE_USERNAME="rjm_app"
$env:RJM_DATABASE_PASSWORD="replace-with-strong-password"
$env:RJM_PYTHON_AI_BASE_URL="http://127.0.0.1:8000"
$env:RJM_BOOTSTRAP_INVITE_CODE="replace-with-first-admin-invite"
```

Linux systemd 环境写法：

```ini
Environment=SPRING_PROFILES_ACTIVE=cloud
Environment=RJM_DATABASE_URL=jdbc:postgresql://127.0.0.1:5432/rjm_formula_ai
Environment=RJM_DATABASE_USERNAME=rjm_app
Environment=RJM_DATABASE_PASSWORD=replace-with-strong-password
Environment=RJM_PYTHON_AI_BASE_URL=http://127.0.0.1:8000
Environment=RJM_BOOTSTRAP_INVITE_CODE=replace-with-first-admin-invite
```

### 3. 启动 Java 管理服务

```powershell
cd F:\zky\RJM\apps\java-admin-service
.\mvnw.cmd spring-boot:run -Dspring-boot.run.profiles=cloud
```

或部署 jar：

```powershell
.\mvnw.cmd clean package
java -jar target\management-service-0.1.0-SNAPSHOT.jar --spring.profiles.active=cloud
```

### 4. 云端配置注意事项

- `RJM_DATABASE_PASSWORD`、`RJM_BOOTSTRAP_INVITE_CODE`、Yuxi token、DeepSeek API key 必须放在环境变量或云平台 Secret 中，不要提交到 Git。
- `RJM_BOOTSTRAP_INVITE_CODE` 只用于创建第一个账号；第一个账号登录后应在系统内生成后续邀请码。
- PostgreSQL schema 会通过 `classpath:db/schema.postgresql.sql` 自动执行，SQL 均为 `create table if not exists`，重复启动不会清空数据。
- 云端 Java 服务和 Python AI 服务可以部署在同一台机器，也可以分开部署；分开部署时将 `RJM_PYTHON_AI_BASE_URL` 改成 Python 服务内网地址。
- 生产环境建议只开放 Java 管理服务端口，Python AI 和数据库端口仅允许内网访问。
