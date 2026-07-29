package com.rjm.formulaai.management.persistence;

import javax.sql.DataSource;
import java.math.BigDecimal;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.ArrayList;
import java.util.List;

public class LearnedWeightRepository {
    private final DataSource dataSource;

    public LearnedWeightRepository(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    public void saveWeight(String goal, String targetType, String targetKey, BigDecimal weight,
            int evidenceCount, String source, String calculationNote) {
        Connection connection = null;
        PreparedStatement updateStatement = null;
        PreparedStatement insertStatement = null;
        try {
            connection = dataSource.getConnection();
            updateStatement = connection.prepareStatement("update learned_weight "
                    + "set weight = ?, evidence_count = ?, source = ?, calculation_note = ?, "
                    + "updated_at = current_timestamp "
                    + "where goal = ? and target_type = ? and target_key = ?");
            updateStatement.setDouble(1, weight.doubleValue());
            updateStatement.setInt(2, evidenceCount);
            updateStatement.setString(3, source);
            updateStatement.setString(4, calculationNote);
            updateStatement.setString(5, goal);
            updateStatement.setString(6, targetType);
            updateStatement.setString(7, targetKey);
            if (updateStatement.executeUpdate() > 0) {
                return;
            }

            insertStatement = connection.prepareStatement("insert into learned_weight "
                    + "(goal, target_type, target_key, weight, evidence_count, source, calculation_note) "
                    + "values (?, ?, ?, ?, ?, ?, ?)");
            insertStatement.setString(1, goal);
            insertStatement.setString(2, targetType);
            insertStatement.setString(3, targetKey);
            insertStatement.setDouble(4, weight.doubleValue());
            insertStatement.setInt(5, evidenceCount);
            insertStatement.setString(6, source);
            insertStatement.setString(7, calculationNote);
            insertStatement.executeUpdate();
        } catch (Exception exception) {
            throw new IllegalStateException("Failed to save learned weight", exception);
        } finally {
            closeQuietly(insertStatement);
            closeQuietly(updateStatement);
            closeQuietly(connection);
        }
    }

    public List<LearnedWeightRecord> listWeights(String goal, String targetType) {
        Connection connection = null;
        PreparedStatement statement = null;
        ResultSet rows = null;
        try {
            connection = dataSource.getConnection();
            statement = connection.prepareStatement("select goal, target_type, target_key, weight, "
                    + "evidence_count, source, calculation_note from learned_weight "
                    + "where goal = ? and target_type = ? order by weight desc, target_key asc");
            statement.setString(1, goal);
            statement.setString(2, targetType);
            rows = statement.executeQuery();
            List<LearnedWeightRecord> weights = new ArrayList<LearnedWeightRecord>();
            while (rows.next()) {
                weights.add(new LearnedWeightRecord(
                        rows.getString("goal"),
                        rows.getString("target_type"),
                        rows.getString("target_key"),
                        rows.getBigDecimal("weight"),
                        rows.getInt("evidence_count"),
                        rows.getString("source"),
                        rows.getString("calculation_note")));
            }
            return weights;
        } catch (Exception exception) {
            throw new IllegalStateException("Failed to list learned weights", exception);
        } finally {
            closeQuietly(rows);
            closeQuietly(statement);
            closeQuietly(connection);
        }
    }

    private void closeQuietly(AutoCloseable closeable) {
        if (closeable == null) {
            return;
        }
        try {
            closeable.close();
        } catch (Exception ignored) {
        }
    }
}
