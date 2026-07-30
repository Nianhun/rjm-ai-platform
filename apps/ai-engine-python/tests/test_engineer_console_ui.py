import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
UI_ROOT = ROOT / "apps" / "engineer-console"


class EngineerConsoleUiTest(unittest.TestCase):
    def test_static_console_files_exist(self):
        for relative in ["index.html", "styles.css", "app.js", "README.md"]:
            self.assertTrue((UI_ROOT / relative).exists(), relative)

    def test_console_targets_management_api_workflow(self):
        html = (UI_ROOT / "index.html").read_text(encoding="utf-8")
        script = (UI_ROOT / "app.js").read_text(encoding="utf-8")

        self.assertIn("配方工程师工作台", html)
        self.assertIn("/api/knowledge/status", script)
        self.assertIn("/api/knowledge/governance", script)
        self.assertIn("/api/formulas/recommend", script)
        self.assertIn("/api/formulas/${formulaId}/screenings", script)
        self.assertIn("/api/experiments/feedback", script)
        self.assertIn("/api/experiments/batches", script)
        self.assertIn("/api/reports/feedback-impact", script)
        self.assertIn("/api/procurement/recommend", script)
        self.assertIn("/api/procurement/recommendations/${formulaId}", script)
        self.assertIn("/api/procurement/recommendations/${formulaId}/${ingredientId}/status", script)
        self.assertIn("/api/evidence/${evidenceId}", script)
        self.assertIn("/api/learning/weights", script)
        self.assertIn("/api/formulas/${formulaId}/explanation", script)
        self.assertIn('id="loadLearningExplanation"', html)
        self.assertIn('id="loadSavedProcurement"', html)
        self.assertIn('id="requestProcurementSample"', html)
        self.assertIn('id="loadKnowledgeGovernance"', html)
        self.assertIn('id="createExperimentBatch"', html)
        self.assertIn('id="loadExperimentBatches"', html)
        self.assertIn('id="strategy"', html)
        self.assertIn("strategy: els.strategy.value", script)

    def test_console_does_not_present_local_snapshot_as_product_state(self):
        html = (UI_ROOT / "index.html").read_text(encoding="utf-8")
        script = (UI_ROOT / "app.js").read_text(encoding="utf-8")

        self.assertNotIn('id="loadOffline"', html)
        self.assertNotIn('id="ingredientCount">46', html)
        self.assertNotIn('id="relationCount">316', html)
        self.assertNotIn("offlineKnowledgeStatus", script)
        self.assertNotIn("offlineRecommendation", script)
        self.assertNotIn("已回退到离线推荐样例", script)
        self.assertIn("Yuxi 知识库未连接", script)

    def test_console_defaults_api_base_to_serving_origin_and_auto_refreshes(self):
        html = (UI_ROOT / "index.html").read_text(encoding="utf-8")
        script = (UI_ROOT / "app.js").read_text(encoding="utf-8")

        self.assertIn("http://127.0.0.1:8090", html)
        self.assertIn("defaultApiBase", script)
        self.assertIn("window.location.origin", script)
        self.assertIn("refreshKnowledgeStatus();", script)
        self.assertIn("Yuxi 知识库在线", script)
        self.assertIn("当前推荐原料", script)

    def test_console_inputs_use_placeholders_not_prefilled_demo_values(self):
        html = (UI_ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn('id="goal" placeholder="请输入目标功效，例如保湿、舒缓、屏障修护"', html)
        self.assertIn('id="dosageForm" placeholder="请输入剂型，例如乳液、精华、水凝胶"', html)
        self.assertIn('id="skinFeel" placeholder="请输入肤感偏好，例如清爽不粘、滋润、低油感"', html)
        self.assertIn('id="engineer" placeholder="请输入工程师姓名或工号"', html)
        self.assertIn('<textarea id="screeningReason" placeholder="请输入审核意见、实验关注点或修改依据"></textarea>', html)
        self.assertNotIn('value="保湿"', html)
        self.assertNotIn('value="乳液"', html)
        self.assertNotIn('value="清爽不粘"', html)
        self.assertNotIn('本地演示可留空', html)

    def test_console_has_workbench_status_and_selection_summary(self):
        html = (UI_ROOT / "index.html").read_text(encoding="utf-8")
        script = (UI_ROOT / "app.js").read_text(encoding="utf-8")
        styles = (UI_ROOT / "styles.css").read_text(encoding="utf-8")

        self.assertIn('id="operationStatus"', html)
        self.assertIn('id="selectedFormulaSummary"', html)
        self.assertIn("withActionStatus", script)
        self.assertIn("setActionStatus", script)
        self.assertIn("updateSelectedFormulaSummary", script)
        self.assertIn(".operation-status", styles)
        self.assertIn(".formula-summary", styles)

    def test_console_preserves_header_icon_buttons_during_actions(self):
        script = (UI_ROOT / "app.js").read_text(encoding="utf-8")

        self.assertIn('button.classList.contains("icon-button")', script)
        self.assertIn('button.setAttribute("aria-busy", "true")', script)
        self.assertNotIn('button.innerHTML = "处理中', script)

    def test_console_rail_background_covers_long_pages(self):
        styles = (UI_ROOT / "styles.css").read_text(encoding="utf-8")

        self.assertIn("background: linear-gradient(90deg, var(--primary-900) 0 72px, var(--bg-app) 72px 100%);", styles)
        self.assertIn("background: var(--bg-app);", styles)

    def test_console_uses_single_screen_views(self):
        html = (UI_ROOT / "index.html").read_text(encoding="utf-8")
        script = (UI_ROOT / "app.js").read_text(encoding="utf-8")
        styles = (UI_ROOT / "styles.css").read_text(encoding="utf-8")

        self.assertIn('id="workspaceCore" class="app-view workspace-core active"', html)
        self.assertIn('id="outputPage" class="app-view output-page"', html)
        self.assertIn("overflow: hidden;", styles)
        self.assertIn("setActiveView", script)
        self.assertNotIn("document.querySelector(\".inspector\")?.scrollIntoView", script)

    def test_console_has_yuxi_ai_chat_page(self):
        html = (UI_ROOT / "index.html").read_text(encoding="utf-8")
        script = (UI_ROOT / "app.js").read_text(encoding="utf-8")

        self.assertIn('id="chatPage" class="app-view chat-page"', html)
        self.assertIn('id="chatInput"', html)
        self.assertIn('id="sendChat"', html)
        self.assertIn("/api/ai/chat", script)
        self.assertIn("selected_formula: state.selectedFormula", script)

    def test_console_requires_login_and_validates_registration_inputs(self):
        html = (UI_ROOT / "index.html").read_text(encoding="utf-8")
        script = (UI_ROOT / "app.js").read_text(encoding="utf-8")
        styles = (UI_ROOT / "styles.css").read_text(encoding="utf-8")

        for element_id in ["authShell", "loginEmail", "registerEmail", "registerPassword", "registerInvite", "registerCode"]:
            self.assertIn(f'id="{element_id}"', html)
        self.assertIn("/api/auth/email-code", script)
        self.assertIn("/api/auth/register", script)
        self.assertIn("/api/auth/login", script)
        self.assertIn("Authorization", script)
        self.assertIn("Bearer ${state.sessionToken}", script)
        self.assertIn("当前 Java 服务尚未加载登录接口，请重启 Java Admin 服务后刷新页面。", script)
        self.assertIn("validateAuthField", script)
        self.assertIn(".field-error", styles)

    def test_console_has_history_and_invite_pages(self):
        html = (UI_ROOT / "index.html").read_text(encoding="utf-8")
        script = (UI_ROOT / "app.js").read_text(encoding="utf-8")
        styles = (UI_ROOT / "styles.css").read_text(encoding="utf-8")

        for view_id in ["historyPage", "invitePage"]:
            self.assertIn(f'data-view="{view_id}"', html)
            self.assertIn(f'id="{view_id}"', html)
        self.assertIn("/api/history/formulas", script)
        self.assertIn("/api/history/chats", script)
        self.assertIn("/api/invites", script)
        self.assertIn("renderFormulaHistory", script)
        self.assertIn("renderChatTaskHistory", script)
        self.assertIn("renderInvites", script)
        self.assertIn(".history-page.active", styles)
        self.assertIn(".invite-page.active", styles)

    def test_experiment_learning_and_procurement_are_dedicated_visual_pages(self):
        html = (UI_ROOT / "index.html").read_text(encoding="utf-8")
        script = (UI_ROOT / "app.js").read_text(encoding="utf-8")
        styles = (UI_ROOT / "styles.css").read_text(encoding="utf-8")

        for view_id in ["experimentPage", "learningPage", "procurementPage"]:
            self.assertIn(f'data-view="{view_id}"', html)
            self.assertIn(f'id="{view_id}" class="app-view workflow-page"', html)
        self.assertIn('id="experimentOutput"', html)
        self.assertIn('id="learningOutput"', html)
        self.assertIn('id="procurementOutput"', html)
        self.assertIn("updateWorkflowPageOutput", script)
        self.assertIn("workflow-result", styles)
        self.assertIn("workflow-timeline", styles)

    def test_inspector_keeps_only_formula_review_tabs(self):
        html = (UI_ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn('data-tab="overview"', html)
        self.assertIn('data-tab="formula"', html)
        self.assertIn('data-tab="evidence"', html)
        self.assertNotIn('data-tab="experiment"', html)
        self.assertNotIn('data-tab="learning"', html)
        self.assertNotIn('data-tab="procurement"', html)

    def test_system_settings_is_dedicated_view_not_home_anchor(self):
        html = (UI_ROOT / "index.html").read_text(encoding="utf-8")
        script = (UI_ROOT / "app.js").read_text(encoding="utf-8")
        styles = (UI_ROOT / "styles.css").read_text(encoding="utf-8")

        self.assertIn('data-view="settingsPage"', html)
        self.assertIn('id="settingsPage" class="app-view settings-page"', html)
        self.assertNotIn('data-target="systemSettings"', html)
        self.assertNotIn('id="systemSettings"', html)
        self.assertIn("settingsRefreshKnowledge", script)
        self.assertIn(".settings-page.active", styles)

    def test_console_does_not_duplicate_inspector_tabs_in_left_rail(self):
        html = (UI_ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn('data-view="workspaceCore"', html)
        self.assertNotIn('class="rail-item" type="button" data-target="inspectorExperiment"', html)
        self.assertNotIn('class="rail-item" type="button" data-target="inspectorEvidence"', html)
        self.assertNotIn('class="rail-item" type="button" data-target="inspectorLearning"', html)
        self.assertNotIn('class="rail-item" type="button" data-target="inspectorProcurement"', html)

    def test_candidate_selection_uses_exact_formula_id_not_priority_style(self):
        script = (UI_ROOT / "app.js").read_text(encoding="utf-8")
        styles = (UI_ROOT / "styles.css").read_text(encoding="utf-8")

        self.assertIn("article.dataset.formulaId = formula.id", script)
        self.assertIn("card.dataset.formulaId === formula.id", script)
        self.assertNotIn("card.textContent.includes(formula.id)", script)
        self.assertIn(".candidate-card.priority:not(.selected)", styles)
        self.assertNotIn(".candidate-card.selected,\n.candidate-card.priority", styles)

    def test_parameter_panel_can_collapse_and_scrollbars_are_styled(self):
        html = (UI_ROOT / "index.html").read_text(encoding="utf-8")
        script = (UI_ROOT / "app.js").read_text(encoding="utf-8")
        styles = (UI_ROOT / "styles.css").read_text(encoding="utf-8")

        self.assertIn('id="toggleParameterPanel"', html)
        self.assertIn("function toggleParameterPanel()", script)
        self.assertIn("parameter-collapsed", script)
        self.assertIn(".workspace-core.parameter-collapsed", styles)
        self.assertIn("*::-webkit-scrollbar-thumb", styles)
        self.assertIn("scrollbar-width: thin", styles)

    def test_inspector_column_has_its_own_scroll_area(self):
        styles = (UI_ROOT / "styles.css").read_text(encoding="utf-8")

        self.assertIn(".inspector {", styles)
        self.assertIn("overflow-y: auto;", styles)
        self.assertIn(".inspector-tabs", styles)
        self.assertIn("position: sticky;", styles)

    def test_inspector_formula_table_wraps_long_yuxi_ids_inside_column(self):
        styles = (UI_ROOT / "styles.css").read_text(encoding="utf-8")

        self.assertIn(".mini-table-wrap table", styles)
        self.assertIn("table-layout: fixed;", styles)
        self.assertIn(".mini-table-wrap th:nth-child(1)", styles)
        self.assertIn("overflow-wrap: anywhere;", styles)
        self.assertIn("word-break: break-word;", styles)

    def test_console_copy_is_not_mojibake(self):
        suspicious_fragments = ["閻", "缁", "閸", "瀹稿弶", "闁"]
        for relative in ["index.html", "app.js", "README.md"]:
            content = (UI_ROOT / relative).read_text(encoding="utf-8")
            for fragment in suspicious_fragments:
                self.assertNotIn(fragment, content, relative)


if __name__ == "__main__":
    unittest.main()
