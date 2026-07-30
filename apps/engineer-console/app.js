const state = {
  formulas: [],
  selectedFormula: null,
  activeTab: "overview",
  lastOutput: {},
  generatedAt: "",
  compareMode: false,
  knowledgeLabel: "等待 Yuxi 知识库",
  chatHistory: [],
  currentUser: null,
  sessionToken: localStorage.getItem("rjm_session_token") || "",
};

const testCompatibilityLabels = {
  yuxiOnline: "Yuxi 知识库在线",
  currentIngredients: "当前推荐原料",
};

const strategyLabels = {
  knowledge_graph_ai: "知识图谱 AI",
  baseline: "知识图谱 AI",
  learned_weight: "实验反馈加权",
  exploration: "低风险探索",
};

const els = {
  authShell: document.getElementById("authShell"),
  appShell: document.getElementById("appShell"),
  showLogin: document.getElementById("showLogin"),
  showRegister: document.getElementById("showRegister"),
  loginForm: document.getElementById("loginForm"),
  registerForm: document.getElementById("registerForm"),
  loginEmail: document.getElementById("loginEmail"),
  loginPassword: document.getElementById("loginPassword"),
  registerEmail: document.getElementById("registerEmail"),
  registerPassword: document.getElementById("registerPassword"),
  registerInvite: document.getElementById("registerInvite"),
  registerCode: document.getElementById("registerCode"),
  loginButton: document.getElementById("loginButton"),
  registerButton: document.getElementById("registerButton"),
  sendCodeButton: document.getElementById("sendCodeButton"),
  authStatus: document.getElementById("authStatus"),
  devCodeHint: document.getElementById("devCodeHint"),
  apiBase: document.getElementById("apiBase"),
  apiToken: document.getElementById("apiToken"),
  connectionState: document.getElementById("connectionState"),
  apiStatusLabel: document.getElementById("apiStatusLabel"),
  ingredientCount: document.getElementById("ingredientCount"),
  relationCount: document.getElementById("relationCount"),
  evidenceSummary: document.getElementById("evidenceSummary"),
  currentStrategyLabel: document.getElementById("currentStrategyLabel"),
  goal: document.getElementById("goal"),
  dosageForm: document.getElementById("dosageForm"),
  skinFeel: document.getElementById("skinFeel"),
  strategy: document.getElementById("strategy"),
  blockedIngredients: document.getElementById("blockedIngredients"),
  formulaList: document.getElementById("formulaList"),
  candidateCount: document.getElementById("candidateCount"),
  generatedAt: document.getElementById("generatedAt"),
  boardStrategy: document.getElementById("boardStrategy"),
  knowledgeMode: document.getElementById("knowledgeMode"),
  sortMode: document.getElementById("sortMode"),
  compareModeButton: document.getElementById("compareModeButton"),
  selectedRank: document.getElementById("selectedRank"),
  selectedFormulaId: document.getElementById("selectedFormulaId"),
  selectedFormulaSummary: document.getElementById("selectedFormulaSummary"),
  formulaDetail: document.getElementById("formulaDetail"),
  inspectorTitle: document.getElementById("inspectorTitle"),
  inspectorScore: document.getElementById("inspectorScore"),
  engineer: document.getElementById("engineer"),
  decision: document.getElementById("decision"),
  screeningReason: document.getElementById("screeningReason"),
  operationStatus: document.getElementById("operationStatus"),
  structuredOutput: document.getElementById("structuredOutput"),
  outputSummary: document.getElementById("outputSummary"),
  actionOutput: document.getElementById("actionOutput"),
  chatMessages: document.getElementById("chatMessages"),
  chatInput: document.getElementById("chatInput"),
  sendChat: document.getElementById("sendChat"),
  toggleParameterPanel: document.getElementById("toggleParameterPanel"),
  settingsRefreshKnowledge: document.getElementById("settingsRefreshKnowledge"),
  settingsIngredientCount: document.getElementById("settingsIngredientCount"),
  settingsRelationCount: document.getElementById("settingsRelationCount"),
  settingsKnowledgeSource: document.getElementById("settingsKnowledgeSource"),
  experimentFormulaChip: document.getElementById("experimentFormulaChip"),
  learningFormulaChip: document.getElementById("learningFormulaChip"),
  procurementFormulaChip: document.getElementById("procurementFormulaChip"),
  experimentOutput: document.getElementById("experimentOutput"),
  learningOutput: document.getElementById("learningOutput"),
  procurementOutput: document.getElementById("procurementOutput"),
  currentUserLabel: document.getElementById("currentUserLabel"),
  formulaHistoryList: document.getElementById("formulaHistoryList"),
  chatHistoryList: document.getElementById("chatHistoryList"),
  inviteList: document.getElementById("inviteList"),
};

function defaultApiBase() {
  if (window.location.protocol === "http:" || window.location.protocol === "https:") {
    return window.location.origin;
  }
  return "http://127.0.0.1:8090";
}

els.apiBase.value = defaultApiBase();
bindEvents();
renderKnowledgeUnavailable("等待 Yuxi 知识库连接");
renderFormulaInspector(null);
writeOutput({}, "等待接口数据");
bootAuth();

function bindEvents() {
  els.showLogin?.addEventListener("click", () => setAuthMode("login"));
  els.showRegister?.addEventListener("click", () => setAuthMode("register"));
  els.loginButton?.addEventListener("click", login);
  els.registerButton?.addEventListener("click", register);
  els.sendCodeButton?.addEventListener("click", sendEmailCode);
  [els.loginEmail, els.loginPassword, els.registerEmail, els.registerPassword, els.registerInvite, els.registerCode].forEach((input) => {
    input?.addEventListener("blur", () => validateAuthField(input));
    input?.addEventListener("input", () => clearAuthError(input));
  });
  bindAction("refreshHistory", "刷新历史记录", loadHistory);
  bindAction("createInviteButton", "生成邀请码", createInvite);
  bindAction("refreshInvites", "刷新邀请码", loadInvites);
  bindAction("refreshKnowledge", "刷新知识源", refreshKnowledgeStatus);
  bindAction("settingsRefreshKnowledge", "检测知识库连接", refreshKnowledgeStatus);
  bindAction("loadKnowledgeGovernance", "查看知识治理", loadKnowledgeGovernance);
  bindAction("recommendButton", "推荐配方", recommendFormulas);
  bindAction("regenerateButton", "重新推荐", recommendFormulas);
  bindAction("submitScreening", "提交筛选", submitScreening);
  bindAction("submitFeedback", "记录实验反馈", submitFeedback);
  bindAction("createExperimentBatch", "创建实验批次", createExperimentBatch);
  bindAction("loadExperimentBatches", "查看实验批次", loadExperimentBatches);
  bindAction("loadReport", "查看反馈影响", loadFeedbackImpact);
  bindAction("loadProcurement", "生成采购建议", loadProcurement);
  bindAction("loadSavedProcurement", "查看已存采购", loadSavedProcurement);
  bindAction("requestProcurementSample", "申请采购样品", requestProcurementSample);
  bindAction("loadLearningExplanation", "查看学习解释", loadLearningExplanation);
  bindAction("loadLearnedWeights", "查看学习权重", loadLearnedWeights);

  document.getElementById("rejectFormula").addEventListener("click", () => quickScreen("reject"));
  document.getElementById("modifyFormula").addEventListener("click", () => quickScreen("modify"));
  document.getElementById("copyDebug").addEventListener("click", copyDebugOutput);
  document.getElementById("clearDebug").addEventListener("click", () => writeOutput({}, "已清空"));
  els.toggleParameterPanel.addEventListener("click", toggleParameterPanel);
  els.sendChat.addEventListener("click", () => withActionStatus(els.sendChat, "AI 对话", sendChatMessage));
  document.querySelectorAll(".inspector-tab").forEach((tab) => {
    tab.addEventListener("click", () => setInspectorTab(tab.dataset.tab));
  });
  document.querySelectorAll(".rail-item").forEach((item) => {
    item.addEventListener("click", () => navigateRail(item));
  });
  els.strategy.addEventListener("change", () => {
    els.currentStrategyLabel.textContent = strategyLabel(els.strategy.value);
    els.boardStrategy.textContent = `${strategyLabel(els.strategy.value)} 策略`;
  });
  els.sortMode.addEventListener("change", () => renderRecommendations({ formulas: state.formulas, strategy: els.currentStrategyLabel.textContent }));
  els.compareModeButton.addEventListener("click", () => {
    state.compareMode = !state.compareMode;
    els.compareModeButton.setAttribute("aria-pressed", String(state.compareMode));
    els.compareModeButton.classList.toggle("active", state.compareMode);
    setActionStatus(state.compareMode ? "对比模式已开启：候选卡显示完整评分维度。" : "对比模式已关闭。", "success");
  });
}

function bindAction(id, label, action) {
  const button = document.getElementById(id);
  if (button) {
    button.addEventListener("click", (event) => withActionStatus(event.currentTarget, label, action));
  }
}

async function bootAuth() {
  showAuthenticatedApp(false);
  if (!state.sessionToken) {
    showAuthStatus("请登录后访问系统。", "idle");
    return;
  }
  try {
    const me = await requestJson("/api/auth/me");
    state.currentUser = me.email;
    showAuthenticatedApp(true);
    await refreshKnowledgeStatus();
    await loadHistory();
    await loadInvites();
  } catch (error) {
    state.sessionToken = "";
    localStorage.removeItem("rjm_session_token");
    showAuthenticatedApp(false);
    showAuthStatus(error.message || "登录已过期，请重新登录。", "error");
  }
}

function showAuthenticatedApp(authenticated) {
  els.authShell?.classList.toggle("hidden", authenticated);
  els.appShell?.classList.toggle("is-auth-hidden", !authenticated);
  if (els.currentUserLabel) {
    els.currentUserLabel.textContent = authenticated && state.currentUser ? `当前账号：${state.currentUser}` : "未登录";
  }
}

function setAuthMode(mode) {
  const login = mode === "login";
  els.showLogin?.classList.toggle("active", login);
  els.showRegister?.classList.toggle("active", !login);
  els.loginForm?.classList.toggle("active", login);
  els.registerForm?.classList.toggle("active", !login);
  showAuthStatus("", "idle");
}

async function login() {
  try {
    if (!validateAuthFields([els.loginEmail, els.loginPassword])) return;
    showAuthStatus("登录中...", "loading");
    const payload = await requestJson("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email: els.loginEmail.value.trim(), password: els.loginPassword.value }),
    });
    await acceptSession(payload);
  } catch (error) {
    showAuthStatus(error.message, "error");
  }
}

async function register() {
  try {
    if (!validateAuthFields([els.registerEmail, els.registerPassword, els.registerInvite, els.registerCode])) return;
    showAuthStatus("注册中...", "loading");
    const payload = await requestJson("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({
        email: els.registerEmail.value.trim(),
        password: els.registerPassword.value,
        invite_code: els.registerInvite.value.trim(),
        verification_code: els.registerCode.value.trim(),
      }),
    });
    await acceptSession(payload);
  } catch (error) {
    showAuthStatus(error.message, "error");
  }
}

async function sendEmailCode() {
  try {
    if (!validateAuthFields([els.registerEmail])) return;
    showAuthStatus("发送验证码中...", "loading");
    const payload = await requestJson("/api/auth/email-code", {
      method: "POST",
      body: JSON.stringify({ email: els.registerEmail.value.trim() }),
    });
    els.devCodeHint.textContent = payload.dev_code ? `本地开发验证码：${payload.dev_code}` : "验证码已发送，请查收邮箱。";
    showAuthStatus("验证码已发送。", "success");
  } catch (error) {
    showAuthStatus(error.message, "error");
  }
}

async function acceptSession(payload) {
  state.sessionToken = payload.token;
  state.currentUser = payload.email;
  localStorage.setItem("rjm_session_token", state.sessionToken);
  showAuthenticatedApp(true);
  showAuthStatus("", "idle");
  await refreshKnowledgeStatus();
  await loadHistory();
  await loadInvites();
}

function validateAuthFields(inputs) {
  return inputs.map((input) => validateAuthField(input)).every(Boolean);
}

function validateAuthField(input) {
  if (!input) return true;
  const value = input.value.trim();
  let message = "";
  if ((input.id === "loginEmail" || input.id === "registerEmail") && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(value)) {
    message = "账号必须使用邮箱。";
  }
  if ((input.id === "loginPassword" || input.id === "registerPassword") && !value) {
    message = "请输入密码。";
  }
  if (input.id === "registerPassword" && !/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{6,}$/.test(value)) {
    message = "密码至少 6 位，并且必须包含英文大写、小写和数字。";
  }
  if (input.id === "registerInvite" && !value) {
    message = "请输入一次性邀请码。";
  }
  if (input.id === "registerCode" && !/^\d{6}$/.test(value)) {
    message = "请输入 6 位邮箱验证码。";
  }
  setAuthFieldError(input, message);
  return !message;
}

function clearAuthError(input) {
  setAuthFieldError(input, "");
}

function setAuthFieldError(input, message) {
  const error = document.querySelector(`[data-error-for="${input.id}"]`);
  if (error) error.textContent = message;
  input.classList.toggle("invalid", Boolean(message));
}

function showAuthStatus(message, tone = "idle") {
  if (!els.authStatus) return;
  els.authStatus.textContent = message;
  els.authStatus.dataset.tone = tone;
}

function apiBase() {
  return els.apiBase.value.replace(/\/$/, "");
}

async function requestJson(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  const token = els.apiToken?.value.trim();
  if (token) {
    headers["X-RJM-API-Token"] = token;
  }
  if (state.sessionToken) {
    headers.Authorization = `Bearer ${state.sessionToken}`;
  }
  const response = await fetch(`${apiBase()}${path}`, { ...options, headers });
  const text = await response.text();
  let payload = {};
  if (text) {
    try {
      payload = JSON.parse(text);
    } catch (error) {
      throw new Error("API 未启动或返回了非 JSON 响应，请确认 Java 管理服务地址。");
    }
  }
  if (!response.ok) {
    if (response.status === 401 || response.status === 403) {
      state.sessionToken = "";
      localStorage.removeItem("rjm_session_token");
      showAuthenticatedApp(false);
      throw new Error(payload.error || "请登录后再访问");
    }
    if (response.status === 404 && path.startsWith("/api/auth/")) {
      throw new Error("当前 Java 服务尚未加载登录接口，请重启 Java Admin 服务后刷新页面。");
    }
    throw new Error(payload.error || payload.message || `HTTP ${response.status}`);
  }
  return payload;
}

async function withActionStatus(button, label, action) {
  const isIconButton = button.classList.contains("icon-button");
  const originalText = button.textContent;
  button.disabled = true;
  button.setAttribute("aria-busy", "true");
  if (!isIconButton) {
    button.textContent = "处理中...";
  }
  setActionStatus(`${label}中`, "loading");
  try {
    await action();
    setActionStatus(`${label}完成`, "success");
  } catch (error) {
    setActionStatus(`${label}失败：${error.message}`, "error");
    writeOutput({ error: error.message }, "请求失败");
  } finally {
    button.disabled = false;
    button.removeAttribute("aria-busy");
    if (!isIconButton) {
      button.textContent = originalText;
    }
  }
}

function setActionStatus(message, tone = "idle") {
  els.operationStatus.textContent = message;
  els.operationStatus.dataset.tone = tone;
}

function setApiStatus(label, kind = "neutral") {
  els.apiStatusLabel.textContent = label;
  els.apiStatusLabel.dataset.kind = kind;
}

async function refreshKnowledgeStatus() {
  try {
    const status = await requestJson("/api/knowledge/status");
    renderKnowledgeStatus(status, knowledgeConnectionLabel(status));
    writeOutput(status, "知识源状态");
    setApiStatus("API 已连接", "success");
  } catch (error) {
    renderKnowledgeUnavailable("Yuxi 知识库未连接");
    writeOutput({ error: error.message }, "知识库不可用");
    setApiStatus("API 未启动", "warning");
    setActionStatus("无法连接 Java API 或 Yuxi 知识库。请启动在线知识库后刷新。", "offline");
  }
}

async function loadKnowledgeGovernance() {
  try {
    const governance = await requestJson("/api/knowledge/governance");
    renderKnowledgeStatus(governance, knowledgeConnectionLabel(governance));
    writeOutput(governance, "知识治理摘要");
    setApiStatus("API 已连接", "success");
  } catch (error) {
    renderKnowledgeUnavailable("Yuxi 知识库未连接");
    writeOutput({ error: error.message }, "知识治理不可用");
    setApiStatus("知识库不可用", "warning");
  }
}

function knowledgeConnectionLabel(status) {
  const yuxiGraph = status.yuxi_graph || {};
  if (yuxiGraph.online) {
    return testCompatibilityLabels.yuxiOnline;
  }
  return "Yuxi 知识库未连接";
}

async function recommendFormulas() {
  const goal = requireField(els.goal, "请输入目标功效");
  const dosageForm = requireField(els.dosageForm, "请输入剂型");
  const payload = {
    id: `REQ-UI-${Date.now()}`,
    goal,
    dosage_form: dosageForm,
    constraints: {
      preferred_skin_feel: els.skinFeel.value.trim(),
      strategy: els.strategy.value,
      blocked_ingredient_ids: splitCsv(els.blockedIngredients.value),
    },
  };
  renderSkeletonCandidates();
  try {
    const recommendation = await requestJson("/api/formulas/recommend", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    renderRecommendations(recommendation);
    writeOutput(recommendation, "推荐结果");
    setApiStatus("API 已连接", "success");
  } catch (error) {
    renderRecommendations({ formulas: [], strategy: els.strategy.value });
    writeOutput({ error: error.message }, "推荐请求失败");
    setApiStatus("知识库不可用", "warning");
    setActionStatus("推荐失败。请确认 Java API 与在线 Yuxi 知识库均已连接。", "offline");
  }
}

async function submitScreening() {
  const formulaId = currentFormulaId();
  if (!formulaId) {
    throw new Error("请先生成并选择配方");
  }
  const payload = {
    engineer: requireField(els.engineer, "请输入工程师姓名或工号"),
    decision: els.decision.value,
    reason: els.screeningReason.value.trim(),
    modified_ingredients: [],
  };
  const result = await requestJson(`/api/formulas/${formulaId}/screenings`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
  writeOutput(result, "筛选记录已提交");
}

async function submitFeedback() {
  const formula = state.selectedFormula || state.formulas[0];
  const formulaId = currentFormulaId();
  if (!formulaId || !formula) {
    throw new Error("请先生成并选择配方");
  }
  const payload = {
    formula_id: formulaId,
    batch_no: `BATCH-UI-${Date.now()}`,
    result: "pass",
    ingredient_ids: (formula?.ingredients || []).map((item) => item.ingredient_id),
    metrics: { stability: "pass", moisturizing_score: 0.86 },
    issues: [],
    engineer: requireField(els.engineer, "请输入工程师姓名或工号"),
    engineer_conclusion: "小试通过，进入下一轮优化。该结论仅代表本批次实验反馈。",
  };
  const result = await requestJson("/api/experiments/feedback", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  writeOutput(result, "实验反馈已提交");
}

async function createExperimentBatch() {
  const formulaId = currentFormulaId();
  if (!formulaId) {
    throw new Error("请先生成并选择配方");
  }
  const payload = {
    batch_no: `BATCH-UI-${Date.now()}`,
    formula_id: formulaId,
    stage: "lab_trial",
    owner: requireField(els.engineer, "请输入工程师姓名或工号"),
    metrics: { target_hydration_after_2h: 30, target_stability_hours: 48 },
    issues: [],
    conclusion: "已创建小试批次，等待实验反馈。",
    status: "running",
  };
  const result = await requestJson("/api/experiments/batches", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  writeOutput(result, "实验批次已创建");
}

async function loadExperimentBatches() {
  const formulaId = currentFormulaId();
  const result = await requestJson(`/api/experiments/batches?formula_id=${encodeURIComponent(formulaId)}`);
  writeOutput(result, "实验批次列表");
}

async function loadFeedbackImpact() {
  const goal = requireField(els.goal, "请输入目标功效");
  const dosageForm = requireField(els.dosageForm, "请输入剂型");
  const payload = {
    id: `REQ-REPORT-UI-${Date.now()}`,
    goal,
    dosage_form: dosageForm,
    constraints: { strategy: els.strategy.value },
  };
  const result = await requestJson("/api/reports/feedback-impact", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  writeOutput(result, "反馈影响报告");
}

async function loadProcurement() {
  const formula = state.selectedFormula || state.formulas[0];
  if (!formula) {
    writeOutput({ error: "请先选择一个配方" }, "未选择配方");
    setActionStatus("请先选择一个配方，再生成采购建议。", "warning");
    return;
  }
  const result = await requestJson("/api/procurement/recommend", {
    method: "POST",
    body: JSON.stringify({ formula }),
  });
  writeOutput(result, "采购建议");
}

async function loadSavedProcurement() {
  const formulaId = currentFormulaId();
  const result = await requestJson(`/api/procurement/recommendations/${formulaId}`);
  writeOutput(result, "已存采购记录");
}

async function requestProcurementSample() {
  const formulaId = currentFormulaId();
  const ingredientId = currentIngredientId();
  if (!ingredientId) {
    writeOutput({ error: "当前配方没有可申请样品的原料", formula_id: formulaId }, "无可申请原料");
    setActionStatus("当前配方没有可申请样品的原料。", "warning");
    return;
  }
  const result = await requestJson(`/api/procurement/recommendations/${formulaId}/${ingredientId}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status: "sample_requested" }),
  });
  writeOutput(result, "样品申请状态");
}

async function loadLearningExplanation() {
  const formulaId = currentFormulaId();
  if (!formulaId) {
    throw new Error("请先生成并选择配方");
  }
  const goal = requireField(els.goal, "请输入目标功效");
  const result = await requestJson(`/api/formulas/${formulaId}/explanation?goal=${encodeURIComponent(goal)}`);
  writeOutput(result, "学习解释");
}

async function loadLearnedWeights() {
  const goal = requireField(els.goal, "请输入目标功效");
  const result = await requestJson(`/api/learning/weights?goal=${encodeURIComponent(goal)}`);
  writeOutput(result, "学习权重");
}

async function sendChatMessage() {
  const message = requireField(els.chatInput, "请输入要咨询 AI 的配方问题");
  els.chatInput.value = "";
  appendChatMessage("user", message);
  appendChatMessage("assistant", "AI 正在读取 Yuxi 知识图谱并分析...");
  const payload = {
    id: `CHAT-UI-${Date.now()}`,
    message,
    history: state.chatHistory.slice(-10),
    context: {
      goal: els.goal.value.trim(),
      dosage_form: els.dosageForm.value.trim(),
      selected_formula: state.selectedFormula,
    },
  };
  const result = await requestJson("/api/ai/chat", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  removePendingChatMessage();
  appendChatMessage("assistant", result.answer, result);
  state.chatHistory.push({ role: "user", content: message });
  state.chatHistory.push({ role: "assistant", content: result.answer });
  writeOutput(result, "AI 知识问答");
}

async function loadHistory() {
  if (!state.sessionToken) return;
  const formulaHistory = await requestJson("/api/history/formulas");
  const chatTaskHistory = await requestJson("/api/history/chats");
  renderFormulaHistory(formulaHistory.items || []);
  renderChatTaskHistory(chatTaskHistory.items || []);
}

async function loadInvites() {
  if (!state.sessionToken) return;
  const payload = await requestJson("/api/invites");
  renderInvites(payload.items || []);
}

async function createInvite() {
  const payload = await requestJson("/api/invites", { method: "POST", body: JSON.stringify({}) });
  await loadInvites();
  writeOutput(payload, "邀请码已生成");
}

function renderFormulaHistory(items) {
  if (!els.formulaHistoryList) return;
  if (!items.length) {
    els.formulaHistoryList.textContent = "暂无配方任务记录";
    return;
  }
  els.formulaHistoryList.innerHTML = items.map((item) => {
    const count = item.response_json?.formulas?.length ?? 0;
    return `<article class="history-item">
      <strong>${escapeHtml(item.goal || "未命名目标")}</strong>
      <span>${escapeHtml(item.dosage_form || "-")} · ${count} 套候选 · ${escapeHtml(item.created_at || "")}</span>
      <button type="button" data-history-request="${escapeAttr(item.request_id || "")}">查看响应</button>
    </article>`;
  }).join("");
  els.formulaHistoryList.querySelectorAll("[data-history-request]").forEach((button, index) => {
    button.addEventListener("click", () => {
      writeOutput(items[index].response_json || items[index], "配方任务历史响应");
      navigateToOutput();
    });
  });
}

function renderChatTaskHistory(items) {
  if (!els.chatHistoryList) return;
  if (!items.length) {
    els.chatHistoryList.textContent = "暂无对话记录";
    return;
  }
  els.chatHistoryList.innerHTML = items.map((item, index) => {
    return `<article class="history-item">
      <strong>${escapeHtml(summaryText(item.message || "未命名问题", 42))}</strong>
      <span>${escapeHtml(summaryText(item.answer || "-", 96))}</span>
      <button type="button" data-chat-history="${index}">查看对话</button>
    </article>`;
  }).join("");
  els.chatHistoryList.querySelectorAll("[data-chat-history]").forEach((button, index) => {
    button.addEventListener("click", () => {
      writeOutput(items[index].response_json || items[index], "AI 对话历史响应");
      navigateToOutput();
    });
  });
}

function renderInvites(items) {
  if (!els.inviteList) return;
  if (els.currentUserLabel) {
    els.currentUserLabel.textContent = state.currentUser ? `当前账号：${state.currentUser}` : "未登录";
  }
  if (!items.length) {
    els.inviteList.textContent = "暂无邀请码";
    return;
  }
  els.inviteList.innerHTML = items.map((item) => `<article class="invite-item ${item.used ? "used" : ""}">
    <strong>${escapeHtml(item.code)}</strong>
    <span>${item.used ? `已使用：${escapeHtml(item.used_by_email || "-")}` : "未使用"}</span>
    <small>创建时间：${escapeHtml(item.created_at || "-")}${item.used_at ? ` · 使用时间：${escapeHtml(item.used_at)}` : ""}</small>
  </article>`).join("");
}

function navigateToOutput() {
  document.querySelectorAll(".rail-item").forEach((button) => button.classList.toggle("active", button.dataset.view === "outputPage"));
  setActiveView("outputPage");
}

function renderKnowledgeStatus(status, label) {
  const yuxiGraph = status.yuxi_graph || {};
  if (!yuxiGraph.online) {
    renderKnowledgeUnavailable("Yuxi 知识库未连接");
    return;
  }
  state.knowledgeLabel = "使用 Yuxi 知识图谱";
  els.connectionState.textContent = label;
  els.connectionState.dataset.kind = "online";
  els.ingredientCount.textContent = formatNumber(yuxiGraph.entity_count ?? 0);
  els.relationCount.textContent = formatNumber(yuxiGraph.relationship_count ?? 0);
  els.settingsIngredientCount.textContent = formatNumber(yuxiGraph.entity_count ?? 0);
  els.settingsRelationCount.textContent = formatNumber(yuxiGraph.relationship_count ?? 0);
  els.settingsKnowledgeSource.textContent = knowledgeSourceText(status.knowledge_source);
  els.evidenceSummary.textContent = `分块 ${formatNumber(yuxiGraph.indexed_chunks ?? 0)}/${formatNumber(yuxiGraph.total_chunks ?? 0)}`;
  els.currentStrategyLabel.textContent = strategyLabel(els.strategy.value);
  els.knowledgeMode.textContent = state.knowledgeLabel;
  if ((status.warnings || []).length) {
    renderStructuredCards("知识治理提示", [
      { title: "风险边界", body: status.warnings.join("；"), tone: "warning" },
      { title: "治理备注", body: (status.governance_notes || []).join("；") || "暂无治理备注" },
    ]);
  }
}

function renderKnowledgeUnavailable(label) {
  state.knowledgeLabel = "Yuxi 知识库未连接";
  els.connectionState.textContent = label;
  els.connectionState.dataset.kind = "warning";
  els.ingredientCount.textContent = "--";
  els.relationCount.textContent = "--";
  els.settingsIngredientCount.textContent = "--";
  els.settingsRelationCount.textContent = "--";
  els.settingsKnowledgeSource.textContent = "Yuxi 知识库未连接";
  els.evidenceSummary.textContent = "等待 Yuxi";
  els.knowledgeMode.textContent = state.knowledgeLabel;
}

function renderRecommendations(recommendation) {
  state.formulas = sortedFormulas(recommendation.formulas || []);
  state.selectedFormula = state.formulas.find((item) => item.id === state.selectedFormula?.id) || state.formulas[0] || null;
  state.generatedAt = new Date().toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit" });
  els.formulaList.innerHTML = "";
  els.candidateCount.textContent = `${state.formulas.length} 套候选`;
  els.boardStrategy.textContent = `${strategyLabel(recommendation.strategy || els.strategy.value)} 策略`;
  els.currentStrategyLabel.textContent = strategyLabel(recommendation.strategy || els.strategy.value);
  els.generatedAt.textContent = `生成 ${state.generatedAt}`;
  els.knowledgeMode.textContent = state.knowledgeLabel;

  if (!state.formulas.length) {
    els.formulaList.appendChild(renderEmptyState("暂无候选配方。请检查目标功效、禁用原料或 API 连接状态。"));
    renderFormulaInspector(null);
    return;
  }

  state.formulas.forEach((formula, index) => {
    els.formulaList.appendChild(renderCandidateCard(formula, index, recommendation.strategy));
  });
  renderFormulaInspector(state.selectedFormula);
}

function renderSkeletonCandidates() {
  els.formulaList.innerHTML = "";
  for (let index = 0; index < 3; index += 1) {
    const node = document.createElement("div");
    node.className = "candidate-card";
    node.innerHTML = `<div class="candidate-rank"><span class="rank-number">--</span></div><div class="candidate-main"><div class="empty-state">候选方案生成中...</div></div><div class="candidate-score"><div class="score-ring"><span>--</span></div></div>`;
    els.formulaList.appendChild(node);
  }
}

function renderCandidateCard(formula, index, responseStrategy) {
  const article = document.createElement("article");
  const selected = state.selectedFormula?.id === formula.id;
  article.className = `candidate-card${selected ? " selected" : ""}${index === 0 ? " priority" : ""}`;
  article.dataset.formulaId = formula.id;
  article.tabIndex = 0;
  article.setAttribute("role", "button");
  article.setAttribute("aria-pressed", selected ? "true" : "false");
  article.addEventListener("click", () => selectFormula(formula));
  article.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      selectFormula(formula);
    }
  });

  const rank = document.createElement("div");
  rank.className = "candidate-rank";
  rank.innerHTML = `<span class="rank-number">${index + 1}</span>${index === 0 ? '<span class="tag primary">推荐优先验证</span>' : '<span class="tag">候选</span>'}`;

  const main = document.createElement("div");
  main.className = "candidate-main";
  main.innerHTML = `
    <div class="candidate-title">
      <h3 title="${escapeAttr(formula.id)}">${escapeHtml(formula.id)}</h3>
      <span class="state-pill">${screeningLabel(formula.status)}</span>
      <span class="tag">${escapeHtml(strategyLabel(formula.strategy || responseStrategy || "knowledge_graph_ai"))}</span>
      <span class="${riskClass(formula)}">${riskLabel(formula)}</span>
      <span class="tag">${(formula.evidence_ids || []).length} 条证据</span>
    </div>
    ${renderIngredientRows(formula.ingredients || [])}
    <p class="candidate-reason">${escapeHtml(summaryText(formula.recommendation_reason || "暂无推荐理由", 76))}</p>
    <p class="candidate-risk">风险：${escapeHtml((formula.risk_notes || []).join("；") || "暂无风险提示，仍需实验与安全评估。")}</p>
  `;
  main.appendChild(renderEvidenceList(formula.evidence_ids || []));

  const score = document.createElement("div");
  score.className = "candidate-score";
  score.innerHTML = `${renderScoreRing(formula.score?.overall)}<div class="micro-scores"></div><button class="view-detail" type="button">查看详情</button>`;
  const micro = score.querySelector(".micro-scores");
  scoreEntries(formula).forEach(([label, value]) => micro.appendChild(scoreItem(label, value)));
  score.querySelector(".view-detail").addEventListener("click", (event) => {
    event.stopPropagation();
    selectFormula(formula);
  });

  article.append(rank, main, score);
  return article;
}

function selectFormula(formula) {
  state.selectedFormula = formula;
  renderFormulaInspector(formula);
  updateWorkflowFormulaChips(formula);
  document.querySelectorAll(".candidate-card").forEach((card) => {
    const selected = card.dataset.formulaId === formula.id;
    card.classList.toggle("selected", selected);
    card.setAttribute("aria-pressed", selected ? "true" : "false");
  });
}

function setInspectorTab(tabName) {
  state.activeTab = tabName;
  document.querySelectorAll(".inspector-tab").forEach((tab) => {
    const active = tab.dataset.tab === tabName;
    tab.classList.toggle("active", active);
    tab.setAttribute("aria-selected", String(active));
  });
  renderFormulaInspector(state.selectedFormula);
}

function renderFormulaInspector(formula) {
  els.formulaDetail.innerHTML = "";
  els.formulaDetail.className = "inspector-body fade-in";
  if (!formula) {
    els.inspectorTitle.textContent = "尚未选择配方";
    els.inspectorScore.textContent = "--";
    els.selectedRank.textContent = "未选择";
    els.selectedFormulaSummary.textContent = "尚未选择配方";
    els.formulaDetail.classList.add("empty-state");
    els.formulaDetail.textContent = "选择一套候选方案后查看详情。";
    updateWorkflowFormulaChips(null);
    return;
  }

  const rank = state.formulas.findIndex((item) => item.id === formula.id) + 1;
  els.selectedFormulaId.value = formula.id;
  els.inspectorTitle.textContent = formula.id;
  els.inspectorScore.textContent = percent(formula.score?.overall);
  els.selectedRank.textContent = rank > 0 ? `排名 #${rank}` : "手动 ID";
  els.selectedFormulaSummary.textContent = `综合评分 ${percent(formula.score?.overall)} · ${screeningLabel(formula.status)} · ${riskLabel(formula)} · 推荐不能替代真实实验。`;
  updateSelectedFormulaSummary(formula);

  const renderers = {
    overview: renderInspectorOverview,
    formula: renderInspectorFormula,
    evidence: renderInspectorEvidence,
  };
  els.formulaDetail.appendChild((renderers[state.activeTab] || renderInspectorOverview)(formula));
}

function updateWorkflowFormulaChips(formula) {
  const label = formula ? `当前配方 ${formula.id}` : "未选择配方";
  [els.experimentFormulaChip, els.learningFormulaChip, els.procurementFormulaChip].forEach((chip) => {
    if (chip) chip.textContent = label;
  });
}

function updateSelectedFormulaSummary(formula) {
  if (!formula) {
    els.selectedFormulaSummary.textContent = "尚未选择配方";
    return;
  }
  els.selectedFormulaSummary.textContent = `综合评分 ${percent(formula.score?.overall)} · ${screeningLabel(formula.status)} · ${riskLabel(formula)} · 推荐不能替代真实实验。`;
}

function renderInspectorOverview(formula) {
  const node = document.createElement("div");
  node.className = "inspector-section";
  node.innerHTML = `
    <section class="info-block"><h3>推荐理由</h3><p>${escapeHtml(formula.recommendation_reason || "暂无推荐理由")}</p></section>
    <section class="info-block"><h3>关键优势</h3><ul class="plain-list">
      <li>综合评分 ${percent(formula.score?.overall)}，适合进入工程师复核。</li>
      <li>包含 ${(formula.ingredients || []).length} 个核心原料，证据入口 ${(formula.evidence_ids || []).length} 条。</li>
      <li>当前策略：${escapeHtml(strategyLabel(formula.strategy || els.strategy.value))}。</li>
    </ul></section>
    <section class="info-block"><h3>风险提示</h3>${riskListHtml(formula)}</section>
    <section class="info-block"><h3>下一步建议</h3><p>先保留并创建小试批次，记录肤感、稳定性和功效指标；通过后再观察学习权重与采购状态。</p></section>
  `;
  return node;
}

function renderInspectorFormula(formula) {
  const node = document.createElement("div");
  node.className = "inspector-section";
  node.innerHTML = `<section class="info-block"><h3>配方明细</h3>${formulaTable(formula)}</section>`;
  return node;
}

function renderInspectorEvidence(formula) {
  const node = document.createElement("div");
  node.className = "inspector-section";
  node.innerHTML = `<section class="info-block"><h3>证据来源</h3><p>证据用于追溯推荐依据，不表示已完成实验验证。</p></section>`;
  node.appendChild(renderEvidenceList(formula.evidence_ids || [], true));
  return node;
}

function renderExperimentPanel() {
  return actionPanel("实验管理", "小试/中试批次和实验反馈从这里进入。", [
    ["createExperimentBatch", "创建实验批次"],
    ["loadExperimentBatches", "批次列表"],
    ["submitFeedback", "提交通过结果"],
    ["loadReport", "反馈影响"],
  ]);
}

function renderLearningPanel() {
  return actionPanel("学习分析", "查看实验反馈如何影响排序和权重；权重只反映已记录反馈，不代表法规或安全结论。", [
    ["loadLearningExplanation", "学习解释"],
    ["loadLearnedWeights", "学习权重"],
    ["loadReport", "排名变化"],
  ]);
}

function renderProcurementPanel() {
  return actionPanel("采购管理", "按选中配方原料查看 SKU、供应商、MOQ、交期和样品状态。", [
    ["loadProcurement", "采购建议"],
    ["loadSavedProcurement", "已存采购"],
    ["requestProcurementSample", "申请样品"],
  ]);
}

function actionPanel(title, description, actions) {
  const node = document.createElement("div");
  node.className = "inspector-section";
  node.innerHTML = `<section class="info-block"><h3>${escapeHtml(title)}</h3><p>${escapeHtml(description)}</p></section>`;
  const buttons = document.createElement("div");
  buttons.className = "button-stack";
  actions.forEach(([targetId, label], index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = index === 0 ? "primary" : "secondary";
    button.textContent = label;
    button.addEventListener("click", () => document.getElementById(targetId).click());
    buttons.appendChild(button);
  });
  node.appendChild(buttons);
  return node;
}

async function loadEvidence(evidenceId) {
  try {
    const evidence = await requestJson(`/api/evidence/${evidenceId}`);
    writeOutput(evidence, "证据详情");
  } catch (error) {
    writeOutput({ error: error.message, evidence_id: evidenceId, hint: "当前知识源可能没有该证据目录记录" }, "未找到证据");
    setActionStatus("未找到证据或 API 不可用，请检查知识源状态。", "warning");
  }
}

function renderEvidenceList(evidenceIds, detailed = false) {
  const evidence = document.createElement("div");
  evidence.className = "evidence-list";
  if (!evidenceIds.length) {
    evidence.appendChild(emptyInline("暂无证据 ID"));
    return evidence;
  }
  evidenceIds.forEach((evidenceId) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = detailed ? `${evidenceId} · 查看详情` : evidenceId;
    button.title = evidenceId;
    button.setAttribute("aria-label", `查看证据 ${evidenceId}`);
    button.addEventListener("click", (event) => {
      event.stopPropagation();
      withActionStatus(button, "查看证据", () => loadEvidence(evidenceId));
    });
    evidence.appendChild(button);
  });
  return evidence;
}

function writeOutput(payload, title = "接口响应") {
  state.lastOutput = payload;
  els.actionOutput.textContent = JSON.stringify(payload, null, 2);
  els.outputSummary.textContent = title;
  renderStructuredOutput(payload, title);
  updateWorkflowPageOutput(payload, title);
}

function renderStructuredOutput(payload, title) {
  els.structuredOutput.innerHTML = "";
  els.structuredOutput.classList.remove("empty-state");
  if (!payload || Object.keys(payload).length === 0) {
    els.structuredOutput.classList.add("empty-state");
    els.structuredOutput.textContent = "暂无接口响应。";
    return;
  }
  if (payload.error) {
    renderStructuredCards("错误摘要", [
      { title: "请求结果", body: humanError(payload), tone: "danger" },
      { title: "处理建议", body: errorHint(payload) },
    ]);
    return;
  }
  if (Array.isArray(payload.formulas)) return renderFormulaTable(payload.formulas, title);
  if (Array.isArray(payload.items)) return renderProcurementTable(payload);
  if (Array.isArray(payload.batches)) return renderBatchTable(payload);
  if (Array.isArray(payload.rows)) return renderFeedbackImpactTable(payload);
  if (Array.isArray(payload.weights) || Array.isArray(payload.influences)) return renderWeightTable(payload);
  if (payload.id && payload.source_type) return renderEvidenceCard(payload);
  if (payload.stored !== undefined || payload.updated !== undefined) {
    return renderStructuredCards("操作结果", [
      { title: payload.stored || payload.updated ? "已记录" : "未持久化", body: operationResultText(payload), tone: payload.stored || payload.updated ? "success" : "warning" },
    ]);
  }
  renderKeyValuePayload(payload, title);
}

function renderStructuredCards(heading, cards) {
  els.structuredOutput.innerHTML = `<h3>${escapeHtml(heading)}</h3>`;
  cards.forEach((card) => {
    const node = document.createElement("section");
    node.className = "info-block";
    node.innerHTML = `<h3>${escapeHtml(card.title)}</h3><p>${escapeHtml(card.body || "-")}</p>`;
    els.structuredOutput.appendChild(node);
  });
}

function renderFormulaTable(formulas, title) {
  const rows = formulas.map((formula, index) => [`#${index + 1}`, formula.id, percent(formula.score?.overall), strategyLabel(formula.strategy || "-"), ingredientIds(formula).join("、"), (formula.risk_notes || []).join("；") || "暂无风险提示", `${(formula.evidence_ids || []).length} 条`]);
  renderTable(title, ["排名", "配方", "综合分", "策略", "核心原料", "风险摘要", "证据"], rows);
}

function renderProcurementTable(payload) {
  const rows = (payload.items || []).map((item) => {
    const sku = item.recommended_skus?.[0] || {};
    return [item.ingredient_id, procurementStatusText(item.status), sku.sku_id || "-", sku.supplier_id || "-", priceText(sku.price), sku.moq_kg ?? "-", sku.lead_time_days ?? "-", sku.qualification_files?.join("、") || "-"];
  });
  if (!rows.length) {
    els.structuredOutput.classList.add("empty-state");
    els.structuredOutput.textContent = "没有采购记录。DB 模式生成或保存采购建议后可查看持久化状态。";
    return;
  }
  renderTable(`采购状态：${payload.formula_id || currentFormulaId()}`, ["原料", "状态", "SKU", "供应商", "价格", "MOQ kg", "交期 天", "资质"], rows);
}

function renderBatchTable(payload) {
  const rows = (payload.batches || []).map((batch) => [batch.batch_no, batch.formula_id, batch.stage, batch.status || "-", batch.owner, batch.conclusion || "-"]);
  if (!rows.length) {
    els.structuredOutput.classList.add("empty-state");
    els.structuredOutput.textContent = "没有实验批次。请先创建小试或中试批次。";
    return;
  }
  renderTable(`实验批次：${payload.formula_id}`, ["批次", "配方", "阶段", "状态", "负责人", "结论"], rows);
}

function renderFeedbackImpactTable(payload) {
  const rows = (payload.rows || []).map((row) => [row.formula_id, row.baseline_rank ?? "-", row.learned_rank ?? "-", percent(row.baseline_score), percent(row.learned_score), signedPercent(row.score_delta), (row.ingredient_ids || []).join("、")]);
  renderTable(`反馈影响：${payload.feedback_count ?? 0} 条实验反馈`, ["配方", "原排名", "学习后排名", "原分数", "学习后分数", "变化", "原料"], rows);
}

function renderWeightTable(payload) {
  const weights = payload.weights || payload.influences || [];
  if (!weights.length) {
    els.structuredOutput.classList.add("empty-state");
    els.structuredOutput.textContent = "暂无学习权重。只有通过实验反馈并在 DB 模式下持久化后，才会产生可审计权重。";
    return;
  }
  const rows = weights.map((row) => [row.target_type, row.target_key, signedPercent(row.weight), row.evidence_count ?? 0, row.source || "-", row.calculation_note || "-"]);
  renderTable(payload.formula_id ? `学习解释：${payload.formula_id}` : `学习权重：${payload.goal || els.goal.value}`, ["对象", "键", "权重", "证据数", "来源", "计算说明"], rows);
}

function renderEvidenceCard(payload) {
  renderStructuredCards("证据详情", [
    { title: `${payload.id} · ${payload.source_type}`, body: payload.title || "-" },
    { title: "摘要", body: payload.summary || "-" },
    { title: "来源", body: payload.source_url || "-" },
  ]);
}

function renderKeyValuePayload(payload, title) {
  renderTable(title, ["字段", "值"], Object.entries(payload).map(([key, value]) => [key, typeof value === "object" ? JSON.stringify(value) : String(value)]));
}

function renderTable(title, headers, rows) {
  els.structuredOutput.innerHTML = `<h3>${escapeHtml(title)}</h3>`;
  const wrap = document.createElement("div");
  wrap.className = "data-table-wrap";
  const table = document.createElement("table");
  table.innerHTML = `<thead><tr>${headers.map((header) => `<th scope="col">${escapeHtml(header)}</th>`).join("")}</tr></thead><tbody>${rows.map((row) => `<tr>${row.map((cell) => `<td>${escapeHtml(cell)}</td>`).join("")}</tr>`).join("")}</tbody>`;
  wrap.appendChild(table);
  els.structuredOutput.appendChild(wrap);
}

function updateWorkflowPageOutput(payload, title) {
  const target = workflowTargetForTitle(title);
  if (!target) return;
  renderWorkflowPayload(target, payload, title);
}

function workflowTargetForTitle(title) {
  if (/实验|批次|筛选/.test(title)) return els.experimentOutput;
  if (/学习|反馈影响|排名变化/.test(title)) return els.learningOutput;
  if (/采购|样品|SKU/.test(title)) return els.procurementOutput;
  return null;
}

function renderWorkflowPayload(target, payload, title) {
  target.classList.remove("empty-state");
  target.innerHTML = `<h3>${escapeHtml(title)}</h3>`;
  if (!payload || Object.keys(payload).length === 0) {
    target.classList.add("empty-state");
    target.textContent = "暂无业务数据。";
    return;
  }
  if (payload.error) {
    renderWorkflowCards(target, [{ title: "处理失败", body: humanError(payload), tone: "danger" }, { title: "处理建议", body: errorHint(payload) }]);
    return;
  }
  if (Array.isArray(payload.batches)) {
    const rows = payload.batches.map((batch) => [batch.batch_no, batch.formula_id, batch.stage, batch.status || "-", batch.owner, batch.conclusion || "-"]);
    renderWorkflowCards(target, [{ title: "批次数量", body: `${rows.length} 条` }, { title: "当前配方", body: payload.formula_id || currentFormulaId() || "-" }]);
    renderWorkflowTable(target, ["批次", "配方", "阶段", "状态", "负责人", "结论"], rows);
    return;
  }
  if (Array.isArray(payload.items)) {
    const rows = payload.items.map((item) => {
      const sku = item.recommended_skus?.[0] || {};
      return [item.ingredient_id, procurementStatusText(item.status), sku.sku_id || "-", sku.supplier_id || "-", priceText(sku.price), sku.moq_kg ?? "-", sku.lead_time_days ?? "-"];
    });
    renderWorkflowCards(target, [{ title: "原料项", body: `${rows.length} 条` }, { title: "当前配方", body: payload.formula_id || currentFormulaId() || "-" }]);
    renderWorkflowTable(target, ["原料", "状态", "SKU", "供应商", "价格", "MOQ kg", "交期 天"], rows);
    return;
  }
  if (Array.isArray(payload.rows)) {
    const rows = payload.rows.map((row) => [row.formula_id, row.baseline_rank ?? "-", row.learned_rank ?? "-", percent(row.baseline_score), percent(row.learned_score), signedPercent(row.score_delta)]);
    renderWorkflowCards(target, [{ title: "反馈记录", body: `${payload.feedback_count ?? rows.length} 条` }, { title: "目标功效", body: payload.goal || els.goal.value || "-" }]);
    renderWorkflowTable(target, ["配方", "原排名", "学习后排名", "原分数", "学习后分数", "变化"], rows);
    return;
  }
  if (Array.isArray(payload.weights) || Array.isArray(payload.influences)) {
    const weights = payload.weights || payload.influences || [];
    const rows = weights.map((row) => [row.target_type, row.target_key, signedPercent(row.weight), row.evidence_count ?? 0, row.source || "-"]);
    renderWorkflowCards(target, [{ title: "权重项", body: `${rows.length} 条` }, { title: "目标功效", body: payload.goal || els.goal.value || "-" }]);
    renderWorkflowTable(target, ["对象", "键", "权重", "证据数", "来源"], rows);
    return;
  }
  if (payload.stored !== undefined || payload.updated !== undefined) {
    renderWorkflowCards(target, [
      { title: payload.stored || payload.updated ? "状态" : "状态", body: operationResultText(payload), tone: payload.stored || payload.updated ? "success" : "warning" },
    ]);
    return;
  }
  renderWorkflowCards(target, Object.entries(payload).slice(0, 8).map(([key, value]) => ({ title: key, body: typeof value === "object" ? JSON.stringify(value) : String(value) })));
}

function renderWorkflowCards(target, cards) {
  const wrap = document.createElement("div");
  wrap.className = "workflow-summary";
  cards.forEach((card) => {
    const node = document.createElement("section");
    node.className = `workflow-card ${card.tone || ""}`.trim();
    node.innerHTML = `<span>${escapeHtml(card.title)}</span><strong>${escapeHtml(card.body || "-")}</strong>`;
    wrap.appendChild(node);
  });
  target.appendChild(wrap);
}

function renderWorkflowTable(target, headers, rows) {
  if (!rows.length) {
    const empty = document.createElement("p");
    empty.className = "workflow-empty";
    empty.textContent = "暂无记录。";
    target.appendChild(empty);
    return;
  }
  const wrap = document.createElement("div");
  wrap.className = "data-table-wrap workflow-table";
  const table = document.createElement("table");
  table.innerHTML = `<thead><tr>${headers.map((header) => `<th scope="col">${escapeHtml(header)}</th>`).join("")}</tr></thead><tbody>${rows.map((row) => `<tr>${row.map((cell) => `<td>${escapeHtml(cell)}</td>`).join("")}</tr>`).join("")}</tbody>`;
  wrap.appendChild(table);
  target.appendChild(wrap);
}

function quickScreen(decision) {
  els.decision.value = decision;
  if (decision === "reject") els.screeningReason.value = "剔除：风险、证据或工程适配性不足，暂不进入实验。";
  if (decision === "modify") els.screeningReason.value = "要求修改：请调整原料比例或降低风险后重新评估。";
  document.getElementById("submitScreening").click();
}

function navigateRail(item) {
  document.querySelectorAll(".rail-item").forEach((button) => button.classList.remove("active"));
  item.classList.add("active");
  if (item.dataset.view) {
    setActiveView(item.dataset.view);
    return;
  }
  setActiveView("workspaceCore");
  const target = document.getElementById(item.dataset.target);
  if (target?.classList.contains("inspector-tab")) {
    setInspectorTab(target.dataset.tab);
    return;
  }
  target?.focus?.();
}

function setActiveView(viewId) {
  document.querySelectorAll(".app-view").forEach((view) => {
    view.classList.toggle("active", view.id === viewId);
  });
}

function toggleParameterPanel() {
  const workspace = document.getElementById("workspaceCore");
  const collapsed = workspace.classList.toggle("parameter-collapsed");
  els.toggleParameterPanel.setAttribute("aria-expanded", String(!collapsed));
  els.toggleParameterPanel.setAttribute("aria-label", collapsed ? "展开配方任务栏" : "收起配方任务栏");
  els.toggleParameterPanel.title = collapsed ? "展开配方任务栏" : "收起配方任务栏";
  els.toggleParameterPanel.querySelector("span").textContent = collapsed ? "›" : "‹";
}

function appendChatMessage(role, text, payload = null) {
  const node = document.createElement("div");
  node.className = `chat-message ${role}`;
  if (text.includes("AI 正在读取")) {
    node.dataset.pending = "true";
  }
  const meta = payload ? chatMeta(payload) : "";
  node.innerHTML = `<strong>${role === "user" ? "配方师" : "AI"}</strong><p>${escapeHtml(text)}</p>${meta}`;
  els.chatMessages.appendChild(node);
  els.chatMessages.scrollTop = els.chatMessages.scrollHeight;
}

function removePendingChatMessage() {
  els.chatMessages.querySelector('[data-pending="true"]')?.remove();
}

function chatMeta(payload) {
  const evidence = (payload.evidence_ids || []).slice(0, 8).map((id) => `<span>${escapeHtml(id)}</span>`).join("");
  const ingredients = (payload.ingredient_ids || []).slice(0, 8).map((id) => `<span>${escapeHtml(id)}</span>`).join("");
  const graph = payload.yuxi_graph || {};
  return `<div class="chat-meta"><span>${escapeHtml(payload.knowledge_source || "Yuxi")}</span><span>${formatNumber(graph.entity_count || 0)} 实体</span><span>${formatNumber(graph.relationship_count || 0)} 关系</span></div><div class="chat-tags">${ingredients}${evidence}</div>`;
}

function sortedFormulas(formulas) {
  const copy = [...formulas];
  if (els.sortMode.value === "evidence") return copy.sort((a, b) => (b.evidence_ids || []).length - (a.evidence_ids || []).length);
  if (els.sortMode.value === "risk") return copy.sort((a, b) => (a.risk_notes || []).length - (b.risk_notes || []).length);
  return copy.sort((a, b) => Number(b.score?.overall || 0) - Number(a.score?.overall || 0));
}

function renderIngredientRows(ingredients) {
  return `<div class="ingredient-compact">${ingredients.map((item) => `<div class="ingredient-row"><span title="${escapeAttr(item.ingredient_id)}">${escapeHtml(item.role || item.ingredient_id)}</span><span>${escapeHtml(rangeText(item))}</span></div>`).join("")}</div>`;
}

function renderScoreRing(value) {
  const number = Math.max(0, Math.min(100, Math.round(Number(value || 0) * 100)));
  return `<div class="score-ring" style="--score:${number}"><span>${number}%</span></div>`;
}

function formulaTable(formula) {
  const rows = (formula.ingredients || []).map((item) => [item.ingredient_id, item.role || "-", rangeText(item), `${(formula.evidence_ids || []).length}`]);
  return `<div class="mini-table-wrap"><table><thead><tr><th>原料</th><th>角色</th><th>建议比例</th><th>证据数</th></tr></thead><tbody>${rows.map((row) => `<tr>${row.map((cell) => `<td>${escapeHtml(cell)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
}

function riskListHtml(formula) {
  const items = (formula.risk_notes || []).length ? formula.risk_notes : ["暂无接口返回风险提示，但仍需真实实验、稳定性、功效、法规与安全评估。"];
  return `<ul class="risk-list">${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
}

function scoreEntries(formula) {
  return [["功效", formula.score?.efficacy], ["稳定", formula.score?.stability], ["肤感", formula.score?.skin_feel], ["成本", formula.score?.cost], ["供应", formula.score?.supply]];
}

function scoreItem(label, value) {
  const item = document.createElement("div");
  const width = Math.max(0, Math.min(100, Math.round(Number(value || 0) * 100)));
  item.className = "score-item";
  item.innerHTML = `<span>${escapeHtml(label)}</span><div class="score-bar" aria-hidden="true"><i style="width:${width}%"></i></div><span>${percent(value)}</span>`;
  return item;
}

function currentFormulaId() {
  return els.selectedFormulaId.value.trim() || state.selectedFormula?.id || "";
}

function currentIngredientId() {
  const formula = state.selectedFormula || state.formulas[0];
  return formula?.ingredients?.[0]?.ingredient_id || "";
}

function splitCsv(value) {
  return value.split(",").map((item) => item.trim()).filter(Boolean);
}

function requireField(input, message) {
  const value = input.value.trim();
  if (!value) {
    input.focus();
    throw new Error(message);
  }
  return value;
}

function percent(value) {
  if (value === undefined || value === null || Number.isNaN(Number(value))) return "-";
  return `${Math.round(Number(value) * 100)}%`;
}

function signedPercent(value) {
  if (value === undefined || value === null || Number.isNaN(Number(value))) return "-";
  const number = Number(value);
  return `${number > 0 ? "+" : ""}${Math.round(number * 100)}%`;
}

function evidenceSummary(counts) {
  const items = Object.entries(counts);
  return items.length ? items.map(([key, value]) => `${key} ${value}`).join(" / ") : "-";
}

function rangeText(item) {
  return `${item.suggested_percent_min ?? "-"}-${item.suggested_percent_max ?? "-"}%`;
}

function ingredientIds(formula) {
  return (formula.ingredients || []).map((item) => item.ingredient_id);
}

function screeningLabel(status) {
  return { ai_recommended: "待工程师审核", candidate: "候选", keep: "保留", reject: "剔除", modify: "要求修改" }[status] || status || "待审核";
}

function riskLabel(formula) {
  const count = (formula.risk_notes || []).length;
  if (!count) return "低风险";
  return count >= 2 ? "需重点复核" : "有风险提示";
}

function riskClass(formula) {
  return (formula.risk_notes || []).length ? "risk-pill" : "risk-pill low";
}

function procurementStatusText(status) {
  return { matched: "已匹配", sample_requested: "已申请样品", sample_received: "样品已到", approved: "已批准", rejected: "已拒绝", missing_supplier: "供应缺口" }[status] || status || "-";
}

function strategyLabel(value) {
  return strategyLabels[value] || value || "知识图谱 AI";
}

function knowledgeSourceText(value) {
  return {
    yuxi_graph_online: "Yuxi 在线知识图谱",
    yuxi_graph: "Yuxi 知识图谱",
    ai_provider: "AI 分析服务",
  }[value] || value || "Yuxi 在线知识图谱";
}

function priceText(price) {
  return price?.amount_per_kg === undefined ? "-" : `${price.currency || "CNY"} ${price.amount_per_kg}/kg`;
}

function operationResultText(payload) {
  if (payload.stored) return `已保存。筛选记录 ${payload.screening_count ?? "-"}，反馈记录 ${payload.feedback_count ?? "-"}。`;
  if (payload.updated) return `${payload.formula_id || currentFormulaId()} / ${payload.ingredient_id || "-"} 状态更新为 ${procurementStatusText(payload.status)}。`;
  return "接口返回未持久化。部分操作仅 DB 模式支持，请检查运行模式。";
}

function humanError(payload) {
  return payload.error || "请求失败";
}

function errorHint(payload) {
  if (payload.error?.includes("Token")) return "检查 API Token 输入框，Token 不会写入调试 JSON。";
  return "确认 Java 管理服务和在线 Yuxi 知识库均已启动。";
}

function renderEmptyState(message) {
  const div = document.createElement("div");
  div.className = "empty-state";
  div.textContent = message;
  return div;
}

function emptyInline(message) {
  const span = document.createElement("span");
  span.className = "tag";
  span.textContent = message;
  return span;
}

function copyDebugOutput() {
  const text = els.actionOutput.textContent;
  if (navigator.clipboard) {
    navigator.clipboard.writeText(text).then(() => setActionStatus("调试 JSON 已复制。", "success")).catch(() => setActionStatus("复制失败，请手动选择调试 JSON。", "warning"));
    return;
  }
  setActionStatus("当前浏览器不支持自动复制，请手动选择调试 JSON。", "warning");
}

function formatNumber(value) {
  return Number(value || 0).toLocaleString("zh-CN");
}

function summaryText(value, maxLength) {
  const text = String(value || "");
  return text.length > maxLength ? `${text.slice(0, maxLength)}...` : text;
}

function escapeHtml(value) {
  return String(value ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

function escapeAttr(value) {
  return escapeHtml(value).replace(/`/g, "&#96;");
}
