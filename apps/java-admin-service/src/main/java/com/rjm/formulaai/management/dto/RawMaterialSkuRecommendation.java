package com.rjm.formulaai.management.dto;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class RawMaterialSkuRecommendation {
    private String skuId;
    private String supplierId;
    private String specification;
    private Map<String, Object> price = new LinkedHashMap<String, Object>();
    private BigDecimal moqKg;
    private int leadTimeDays;
    private List<String> qualificationFiles = new ArrayList<String>();
    private String sampleStatus;
    private BigDecimal qualityRating;
    private BigDecimal procurementScore;

    public RawMaterialSkuRecommendation() {
    }

    public RawMaterialSkuRecommendation(String skuId, String supplierId, String specification, Map<String, Object> price,
            BigDecimal moqKg, int leadTimeDays, List<String> qualificationFiles, String sampleStatus,
            BigDecimal qualityRating, BigDecimal procurementScore) {
        this.skuId = skuId;
        this.supplierId = supplierId;
        this.specification = specification;
        this.price = price;
        this.moqKg = moqKg;
        this.leadTimeDays = leadTimeDays;
        this.qualificationFiles = qualificationFiles;
        this.sampleStatus = sampleStatus;
        this.qualityRating = qualityRating;
        this.procurementScore = procurementScore;
    }

    public String getSkuId() {
        return skuId;
    }

    public void setSkuId(String skuId) {
        this.skuId = skuId;
    }

    public String getSupplierId() {
        return supplierId;
    }

    public void setSupplierId(String supplierId) {
        this.supplierId = supplierId;
    }

    public String getSpecification() {
        return specification;
    }

    public void setSpecification(String specification) {
        this.specification = specification;
    }

    public Map<String, Object> getPrice() {
        return price;
    }

    public void setPrice(Map<String, Object> price) {
        this.price = price;
    }

    public BigDecimal getMoqKg() {
        return moqKg;
    }

    public void setMoqKg(BigDecimal moqKg) {
        this.moqKg = moqKg;
    }

    public int getLeadTimeDays() {
        return leadTimeDays;
    }

    public void setLeadTimeDays(int leadTimeDays) {
        this.leadTimeDays = leadTimeDays;
    }

    public List<String> getQualificationFiles() {
        return qualificationFiles;
    }

    public void setQualificationFiles(List<String> qualificationFiles) {
        this.qualificationFiles = qualificationFiles;
    }

    public String getSampleStatus() {
        return sampleStatus;
    }

    public void setSampleStatus(String sampleStatus) {
        this.sampleStatus = sampleStatus;
    }

    public BigDecimal getQualityRating() {
        return qualityRating;
    }

    public void setQualityRating(BigDecimal qualityRating) {
        this.qualityRating = qualityRating;
    }

    public BigDecimal getProcurementScore() {
        return procurementScore;
    }

    public void setProcurementScore(BigDecimal procurementScore) {
        this.procurementScore = procurementScore;
    }
}
