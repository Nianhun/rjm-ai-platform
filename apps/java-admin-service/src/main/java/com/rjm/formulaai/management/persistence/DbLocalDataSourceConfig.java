package com.rjm.formulaai.management.persistence;

import org.springframework.beans.factory.InitializingBean;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.h2.jdbcx.JdbcDataSource;

import javax.sql.DataSource;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.sql.Connection;
import java.sql.Statement;

@Configuration
@ConditionalOnProperty(prefix = "rjm.local-db", name = "enabled", havingValue = "true")
public class DbLocalDataSourceConfig {
    @Bean
    @ConditionalOnMissingBean(DataSource.class)
    public DataSource localDataSource(
            @Value("${rjm.local-db.url}") String url,
            @Value("${rjm.local-db.username:sa}") String username,
            @Value("${rjm.local-db.password:}") String password) {
        JdbcDataSource dataSource = new JdbcDataSource();
        dataSource.setURL(url);
        dataSource.setUser(username);
        dataSource.setPassword(password);
        return dataSource;
    }

    @Bean
    public InitializingBean localSchemaInitializer(
            DataSource dataSource,
            @Value("${rjm.local-db.schema-path:../../infrastructure/database/java-management/schema.h2.sql}") String schemaPath) {
        return new InitializingBean() {
            @Override
            public void afterPropertiesSet() throws Exception {
                String schema = new String(
                        Files.readAllBytes(Paths.get(schemaPath).toAbsolutePath()),
                        StandardCharsets.UTF_8);
                Connection connection = dataSource.getConnection();
                try {
                    Statement statement = connection.createStatement();
                    try {
                        for (String sql : schema.split(";")) {
                            if (!sql.trim().isEmpty()) {
                                statement.execute(sql);
                            }
                        }
                    } finally {
                        statement.close();
                    }
                } finally {
                    connection.close();
                }
            }
        };
    }
}
