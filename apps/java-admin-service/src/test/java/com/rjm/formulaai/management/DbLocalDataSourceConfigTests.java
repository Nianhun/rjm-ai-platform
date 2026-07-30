package com.rjm.formulaai.management;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

import javax.annotation.Resource;
import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.ResultSet;

import static org.junit.jupiter.api.Assertions.assertEquals;

@SpringBootTest(properties = {
        "rjm.ai-service.mode=db",
        "rjm.auth.enabled=false",
        "rjm.local-db.enabled=true",
        "rjm.local-db.url=jdbc:h2:mem:rjm_local_config;DB_CLOSE_DELAY=-1",
        "rjm.local-db.schema-path=../../infrastructure/database/java-management/schema.h2.sql"
})
class DbLocalDataSourceConfigTests {
    @Resource
    private DataSource dataSource;

    @Test
    void localDbModeCreatesDataSourceAndInitializesSchema() throws Exception {
        Connection connection = dataSource.getConnection();
        try {
            ResultSet rows = connection.createStatement()
                    .executeQuery("select count(*) from information_schema.tables where table_name = 'LEARNED_WEIGHT'");
            try {
                rows.next();
                assertEquals(1, rows.getInt(1));
            } finally {
                rows.close();
            }
        } finally {
            connection.close();
        }
    }
}
