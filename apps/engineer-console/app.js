const state = {
  formulas: [],
  selectedFormula: null,
  activeTab: "overview",
  lastOutput: {},
  generatedAt: "",
  compareMode: false,
  knowledgeLabel: "等待 Yuxi 知识库",
  chatHistory: [],
  elementGraph: null,
  selectedElementNodeId: "",
  currentUser: null,
  sessionToken: localStorage.getItem("rjm_session_token") || "",
  yuxiEntityNamesLoaded: false,
};

const viewRoutes = {
  workspaceCore: "/console/formulas",
  chatPage: "/console/chat",
  elementGraphPage: "/console/elements",
  historyPage: "/console/history",
  invitePage: "/console/invites",
  experimentPage: "/console/experiments",
  learningPage: "/console/learning",
  procurementPage: "/console/procurement",
  outputPage: "/console/output",
  settingsPage: "/console/settings",
  formulaDetailPage: "/console/formula-detail",
};

const routeViews = Object.fromEntries(Object.entries(viewRoutes).map(([viewId, route]) => [route, viewId]));

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

const ingredientNameByYuxiId = {
  "YUXI-0E2DBAF04E4EBAF378F5866FC0887323": "Water",
  "YUXI-9E0989EDE09E665C91365EEB437A3F98": "Glycerin",
  "YUXI-0260B25EDFD72EA3CFEF0C4F39932414": "Butylene Glycol",
  "YUXI-F6E8FED8AC2AAE885151288568079DC0": "Panthenol",
  "YUXI-23A27B7400C84B5583C3E49EE90EA359": "Allantoin",
  "YUXI-A094DBC5182F1B5C6C03D2780599F3AF": "Xanthan Gum",
  "YUXI-A0F1011EC3C6A15ED4DB23D0BD8575A5": "Disodium EDTA",
  "YUXI-DBA175D813DA6EC2320E668F799557E0": "Phenoxyethanol",
  "YUXI-7966F64EE3A94C0C9B5B2DD5B77F11E4": "Methylpropanediol",
  "YUXI-56D91A311E29A7E4C19BA0167AD648CE": "Centella Asiatica Extract",
  "YUXI-E0E18E57E7F2A64CFD17260FEC351B0E": "Chamomilla Recutita (Matricaria) Flower Extract",
  "YUXI-E21170EAA87925357BA1B27A44144CA1": "Glycyrrhiza Glabra (Licorice) Root Extract",
  "YUXI-A0A6D421D90DD023F8DCC97E0475BE6B": "Camellia Sinensis Leaf Extract",
  "YUXI-5CCBC89558449BB24C4D3D6942A04BEC": "Carbomer",
  "YUXI-7C2C5DCAFAFC83FF22535EBBA73EF08F": "Arginine",
  "YUXI-4FB999ECC72D3AC14A060C62CD35434E": "Panax Ginseng Seed Oil",
  "YUXI-0D2E96CD6C76FC2DD9A73FCB148A934A": "Scutellaria Baicalensis Root Extract",
  "YUXI-0D3EAA60C8787A1E8E22D456875598CD": "Rosmarinus Officinalis (Rosemary) Leaf Extract",
  "YUXI-F9E3F4D2FBDE289F287DFDA813070FD6": "Ligularia Fishceri Leaf Extract",
  "YUXI-95DCD3B9C5F53BD288AE43975C3324DA": "Rosa Davurica Bud Extract",
  "YUXI-5EE29C44723877F6BFF76827CC79740D": "Dipotassium Glycyrrhizate",
  "YUXI-F03B9298AE0E43E12442542B998E5F95": "Polygonum Cuspidatum Root Extract",
  "YUXI-737C7BEA39726685EEE48FE81B678254": "Red Ginseng Extract",
  "YUXI-74D24CE8B0494134BA064C00251208BE": "Cordyceps Sinensis Extract",
  "YUXI-901B216CBBC169D760FD517C0308CA43": "Glycerin Polyacrylate",
  "YUXI-7B0B446DC488702184B3A9CEFC4A3F9A": "Sodium Polyacrylate",
  "YUXI-265E60F94073997CCDFDC6BB1C539F7F": "1,2-Hexanediol",
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
  logoutButton: document.getElementById("logoutButton"),
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
  backToFormulaList: document.getElementById("backToFormulaList"),
  formulaDetailPageTitle: document.getElementById("formulaDetailPageTitle"),
  formulaDetailPageSummary: document.getElementById("formulaDetailPageSummary"),
  formulaDetailPageRank: document.getElementById("formulaDetailPageRank"),
  formulaDetailHeroTitle: document.getElementById("formulaDetailHeroTitle"),
  formulaDetailHeroText: document.getElementById("formulaDetailHeroText"),
  formulaDetailPageScore: document.getElementById("formulaDetailPageScore"),
  formulaDetailPageBody: document.getElementById("formulaDetailPageBody"),
  formulaDetailReviewPanel: document.getElementById("formulaDetailReviewPanel"),
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
  elementGraphInput: document.getElementById("elementGraphInput"),
  loadElementGraph: document.getElementById("loadElementGraph"),
  elementGraphCanvas: document.getElementById("elementGraphCanvas"),
  elementGraphDetail: document.getElementById("elementGraphDetail"),
  elementGraphStats: document.getElementById("elementGraphStats"),
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
setActiveView(viewForCurrentRoute(), { replace: true });
renderKnowledgeUnavailable("等待 Yuxi 知识库连接");
renderFormulaInspector(null);
writeOutput({}, "等待接口数据");
renderCandidatePrompt();
bootAuth();

function bindEvents() {
  els.showLogin?.addEventListener("click", () => setAuthMode("login"));
  els.showRegister?.addEventListener("click", () => setAuthMode("register"));
  els.loginButton?.addEventListener("click", login);
  els.registerButton?.addEventListener("click", register);
  els.sendCodeButton?.addEventListener("click", sendEmailCode);
  els.logoutButton?.addEventListener("click", () => withActionStatus(els.logoutButton, "退出登录", logout));
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
  bindAction("loadElementGraph", "解析元素图谱", loadElementGraph);
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

  els.backToFormulaList?.addEventListener("click", () => setActiveView("workspaceCore"));
  document.getElementById("rejectFormula").addEventListener("click", () => quickScreen("reject"));
  document.getElementById("modifyFormula").addEventListener("click", () => quickScreen("modify"));
  document.getElementById("copyDebug").addEventListener("click", copyDebugOutput);
  document.getElementById("clearDebug").addEventListener("click", () => writeOutput({}, "已清空"));
  els.toggleParameterPanel.addEventListener("click", toggleParameterPanel);
  els.sendChat.addEventListener("click", () => withActionStatus(els.sendChat, "AI 对话", sendChatMessage));
  els.elementGraphInput?.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      els.loadElementGraph?.click();
    }
  });
  document.querySelectorAll(".inspector-tab").forEach((tab) => {
    tab.addEventListener("click", () => setInspectorTab(tab.dataset.tab));
  });
  document.querySelectorAll(".rail-item").forEach((item) => {
    item.addEventListener("click", () => navigateRail(item));
  });
  window.addEventListener("popstate", () => setActiveView(viewForCurrentRoute(), { skipHistory: true }));
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
    clearSession();
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

async function logout() {
  const token = state.sessionToken;
  try {
    if (token) {
      await requestJson("/api/auth/logout", { method: "POST" });
    }
  } catch (error) {
    // Local session cleanup still lets the engineer switch accounts if the token already expired.
  } finally {
    clearSession();
    showAuthenticatedApp(false);
    setAuthMode("login");
    els.loginPassword.value = "";
    showAuthStatus("已退出登录，可以切换其他账号。", "success");
  }
}

function clearSession() {
  state.sessionToken = "";
  state.currentUser = null;
  localStorage.removeItem("rjm_session_token");
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
      clearSession();
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
    await refreshYuxiEntityNames();
    writeOutput(status, "知识源状态");
    setApiStatus("API 已连接", "success");
  } catch (error) {
    renderKnowledgeUnavailable("Yuxi 知识库未连接");
    writeOutput({ error: error.message }, "知识库不可用");
    setApiStatus("API 未启动", "warning");
    setActionStatus("无法连接 Java API 或 Yuxi 知识库。请启动在线知识库后刷新。", "offline");
  }
}

async function refreshYuxiEntityNames() {
  try {
    const payload = await requestJson("/api/knowledge/entity-names");
    const changed = applyYuxiEntityNames(payload.entity_names || {});
    state.yuxiEntityNamesLoaded = true;
    if (changed && state.formulas.length) {
      renderRecommendations({ formulas: state.formulas, strategy: els.strategy.value });
    }
  } catch (error) {
    state.yuxiEntityNamesLoaded = false;
  }
}

function applyYuxiEntityNames(entityNames) {
  let changed = false;
  Object.entries(entityNames || {}).forEach(([rawId, rawName]) => {
    const id = normalizeYuxiPublicId(rawId);
    const name = String(rawName || "").trim();
    if (!id || !name || isYuxiInternalId(name)) return;
    if (ingredientNameByYuxiId[id] !== name) {
      ingredientNameByYuxiId[id] = name;
      changed = true;
    }
  });
  return changed;
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
    if (!state.yuxiEntityNamesLoaded) {
      await refreshYuxiEntityNames();
    }
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

async function loadElementGraph() {
  const elementId = requireField(els.elementGraphInput, "请输入元素名或 Yuxi ID");
  renderElementGraphLoading(elementId);
  const graph = await requestJson(`/api/knowledge/elements/${encodeURIComponent(elementId)}/graph`);
  renderElementGraph(graph);
  writeOutput(graph, "配方元素图谱");
}

function renderElementGraphLoading(elementId) {
  if (els.elementGraphStats) els.elementGraphStats.textContent = "解析中";
  if (els.elementGraphCanvas) {
    els.elementGraphCanvas.className = "element-graph-canvas empty-state";
    els.elementGraphCanvas.textContent = `正在从 Yuxi 知识图谱解析 ${elementId} 的一层关系...`;
  }
  if (els.elementGraphDetail) {
    els.elementGraphDetail.className = "element-graph-detail empty-state";
    els.elementGraphDetail.textContent = "等待图谱返回。";
  }
}

function renderElementGraph(graph) {
  state.elementGraph = normalizeElementGraph(graph);
  const normalized = state.elementGraph;
  const stats = normalized.stats || {};
  if (els.elementGraphStats) {
    els.elementGraphStats.textContent = `节点 ${stats.node_count ?? normalized.nodes.length} · 边 ${stats.edge_count ?? normalized.edges.length}`;
  }
  if (!els.elementGraphCanvas || !els.elementGraphDetail) return;
  if (!normalized.nodes.length) {
    els.elementGraphCanvas.className = "element-graph-canvas empty-state";
    els.elementGraphCanvas.textContent = "未找到匹配元素，请换一个元素名或 Yuxi ID。";
    els.elementGraphDetail.className = "element-graph-detail empty-state";
    els.elementGraphDetail.textContent = "暂无节点详情。";
    return;
  }
  els.elementGraphCanvas.className = "element-graph-canvas";
  els.elementGraphCanvas.innerHTML = renderElementGraphSvg(normalized);
  els.elementGraphCanvas.querySelectorAll("[data-element-node]").forEach((node) => {
    node.addEventListener("click", () => selectElementGraphNode(node.dataset.elementNode));
    node.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        selectElementGraphNode(node.dataset.elementNode);
      }
    });
  });
  selectElementGraphNode(normalized.center?.id || normalized.nodes[0]?.id);
}

function normalizeElementGraph(graph) {
  const nodes = (graph?.nodes || []).slice(0, 56).map((node, index) => ({
    id: String(node.id || node.entity_id || `node-${index}`),
    label: node.label || node.name || node.display_name || node.id || `节点 ${index + 1}`,
    type: node.type || node.kind || node.category || "element",
    description: node.description || node.summary || "",
    properties: node.properties || node.attributes || {},
  }));
  const centerInput = graph?.center || nodes[0] || null;
  const centerId = centerInput ? String(centerInput.id || centerInput.entity_id || centerInput.label || centerInput.name || "") : "";
  let center = nodes.find((node) => node.id === centerId);
  if (!center && centerInput) {
    center = {
      id: String(centerInput.id || centerInput.entity_id || "center"),
      label: centerInput.label || centerInput.name || centerInput.id || "中心元素",
      type: centerInput.type || centerInput.kind || "center",
      description: centerInput.description || "",
      properties: centerInput.properties || {},
    };
    nodes.unshift(center);
  }
  const ids = new Set(nodes.map((node) => node.id));
  const edges = (graph?.edges || []).slice(0, 80).map((edge, index) => ({
    source: String(edge.source || edge.source_id || ""),
    target: String(edge.target || edge.target_id || ""),
    label: edge.label || edge.type || edge.relation_type || `关系 ${index + 1}`,
  })).filter((edge) => ids.has(edge.source) && ids.has(edge.target));
  return {
    query: graph?.query || "",
    center: center || nodes[0] || null,
    nodes,
    edges,
    stats: graph?.stats || { node_count: nodes.length, edge_count: edges.length },
  };
}

function renderElementGraphSvg(graph) {
  const width = 920;
  const height = 560;
  const centerX = width / 2;
  const centerY = height / 2;
  const centerId = graph.center?.id || graph.nodes[0]?.id;
  const neighbors = graph.nodes.filter((node) => node.id !== centerId);
  const placed = [
    { ...(graph.nodes.find((node) => node.id === centerId) || graph.nodes[0]), x: centerX, y: centerY, center: true },
    ...neighbors.map((node, index) => {
      const angle = (index / Math.max(1, neighbors.length)) * Math.PI * 2 - Math.PI / 2;
      const ringJitter = index % 3 === 0 ? 0 : index % 3 === 1 ? 24 : -18;
      const radius = Math.min(220, Math.max(145, 118 + neighbors.length * 4)) + ringJitter;
      return { ...node, x: centerX + Math.cos(angle) * radius, y: centerY + Math.sin(angle) * radius, center: false };
    }),
  ];
  const byId = new Map(placed.map((node) => [node.id, node]));
  const edgeMarkup = graph.edges.map((edge, index) => {
    const source = byId.get(edge.source);
    const target = byId.get(edge.target);
    if (!source || !target) return "";
    const midX = (source.x + target.x) / 2;
    const midY = (source.y + target.y) / 2;
    return `<g class="element-graph-edge" style="--edge-index:${index}">
      <line x1="${source.x}" y1="${source.y}" x2="${target.x}" y2="${target.y}"></line>
      <text x="${midX}" y="${midY - 6}">${escapeHtml(summaryText(edge.label, 12))}</text>
    </g>`;
  }).join("");
  const nodeMarkup = placed.map((node, index) => {
    const radius = node.center ? 34 : 15 + (index % 4);
    return `<g class="element-graph-node ${node.center ? "center" : elementNodeClass(node)}" data-element-node="${escapeAttr(node.id)}" tabindex="0" role="button" aria-label="${escapeAttr(node.label)}" style="--node-index:${index}">
      <circle cx="${node.x}" cy="${node.y}" r="${radius}"></circle>
      <text x="${node.x}" y="${node.y + radius + 18}">${escapeHtml(summaryText(node.label, node.center ? 20 : 16))}</text>
      <title>${escapeHtml(node.label)} · ${escapeHtml(node.type)}</title>
    </g>`;
  }).join("");
  return `<svg class="element-graph-svg dynamic-graph" viewBox="0 0 ${width} ${height}" role="img" aria-label="配方元素一层知识图谱">${edgeMarkup}${nodeMarkup}</svg>`;
}

function selectElementGraphNode(nodeId) {
  if (!state.elementGraph || !nodeId) return;
  state.selectedElementNodeId = nodeId;
  els.elementGraphCanvas?.querySelectorAll("[data-element-node]").forEach((node) => {
    node.classList.toggle("selected", node.dataset.elementNode === nodeId);
  });
  const graph = state.elementGraph;
  const node = graph.nodes.find((item) => item.id === nodeId) || graph.center;
  if (!node || !els.elementGraphDetail) return;
  const linkedEdges = graph.edges.filter((edge) => edge.source === node.id || edge.target === node.id);
  els.elementGraphDetail.className = "element-graph-detail";
  els.elementGraphDetail.innerHTML = `
    <div class="element-detail-head">
      <span class="element-node-type">${escapeHtml(node.type || "element")}</span>
      <h3>${escapeHtml(node.label || node.id)}</h3>
      <code>${escapeHtml(node.id)}</code>
    </div>
    <p>${escapeHtml(node.description || "暂无节点描述。")}</p>
    <div class="element-detail-stats">
      <span><strong>${linkedEdges.length}</strong> 直接关系</span>
      <span><strong>${graph.nodes.length}</strong> 一层节点</span>
      <span><strong>${graph.edges.length}</strong> 关系边</span>
    </div>
    ${renderElementRelations(node, linkedEdges, graph.nodes)}
    ${renderElementProperties(node.properties)}
  `;
}

function renderElementRelations(node, edges, nodes) {
  if (!edges.length) return `<section class="element-detail-section"><h4>相关关系</h4><p>暂无直接关系。</p></section>`;
  const byId = new Map(nodes.map((item) => [item.id, item]));
  return `<section class="element-detail-section"><h4>相关关系</h4><ul>${edges.slice(0, 10).map((edge) => {
    const otherId = edge.source === node.id ? edge.target : edge.source;
    const other = byId.get(otherId);
    return `<li><strong>${escapeHtml(edge.label)}</strong><span>${escapeHtml(other?.label || otherId)}</span></li>`;
  }).join("")}</ul></section>`;
}

function renderElementProperties(properties) {
  const entries = Object.entries(properties || {}).filter(([, value]) => value !== undefined && value !== null && value !== "").slice(0, 8);
  if (!entries.length) return "";
  return `<section class="element-detail-section"><h4>节点属性</h4><dl>${entries.map(([key, value]) => `<div><dt>${escapeHtml(key)}</dt><dd>${escapeHtml(Array.isArray(value) ? value.join(", ") : value)}</dd></div>`).join("")}</dl></section>`;
}

function elementNodeClass(node) {
  const value = String(node.type || "").toLowerCase();
  if (value.includes("formula")) return "formula";
  if (value.includes("effect") || value.includes("function")) return "function";
  if (value.includes("ingredient") || value.includes("material")) return "ingredient";
  return `tone-${Math.abs(hashString(node.id || node.label)) % 5}`;
}

function hashString(value) {
  return String(value || "").split("").reduce((hash, char) => ((hash << 5) - hash + char.charCodeAt(0)) | 0, 0);
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
    renderCandidatePrompt("暂无候选配方。请检查目标功效、禁用原料或 API 连接状态。");
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
    node.innerHTML = `<div class="brand-loader" aria-hidden="true"></div><div class="candidate-main"><div class="empty-state">候选方案生成中...</div></div>`;
    els.formulaList.appendChild(node);
  }
}

function renderCandidatePrompt(message = "填写左侧目标功效与剂型后，系统会在这里生成候选配方、评分维度和证据链路。") {
  els.formulaList.innerHTML = "";
  const node = document.createElement("div");
  node.className = "candidate-empty-prompt";
  node.innerHTML = `
    <strong>等待生成候选配方</strong>
    <p>${escapeHtml(message)}</p>
    <div>
      <span>PDRN 修复</span>
      <span>PN 支架结构</span>
      <span>植物 PDRN</span>
      <span>核酸系列</span>
    </div>
  `;
  els.formulaList.appendChild(node);
}

function renderCandidateCard(formula, index, responseStrategy) {
  const article = document.createElement("article");
  const selected = state.selectedFormula?.id === formula.id;
  const displayName = formulaDisplayName(formula, index);
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
      <h3 title="${escapeAttr(formula.id)}">${escapeHtml(displayName)}</h3>
      <span class="state-pill">${screeningLabel(formula.status)}</span>
      <span class="tag">${escapeHtml(strategyLabel(formula.strategy || responseStrategy || "knowledge_graph_ai"))}</span>
      <span class="${riskClass(formula)}">${riskLabel(formula)}</span>
      <span class="tag">${(formula.evidence_ids || []).length} 条证据</span>
    </div>
    ${renderIngredientRows(formula.ingredients || [])}
    <p class="candidate-reason">${escapeHtml(summaryText(formula.recommendation_reason || "暂无推荐理由", 76))}</p>
    <p class="candidate-risk">风险：${escapeHtml((formula.risk_notes || []).join("；") || "暂无风险提示，仍需实验与安全评估。")}</p>
  `;
  main.appendChild(renderFormulaEvidenceList(formula));

  const score = document.createElement("div");
  score.className = "candidate-score";
  score.innerHTML = `${renderScoreRing(formula.score?.overall)}<div class="micro-scores"></div><button class="view-detail" type="button">查看详情</button>`;
  const micro = score.querySelector(".micro-scores");
  scoreEntries(formula).forEach(([label, value]) => micro.appendChild(scoreItem(label, value)));
  score.querySelector(".view-detail").addEventListener("click", (event) => {
    event.stopPropagation();
    openFormulaDetailPage(formula, index);
  });

  article.append(rank, main, score);
  return article;
}

function openFormulaDetailPage(formula, index) {
  selectFormula(formula);
  renderFormulaDetailPage(formula, index);
  setActiveView("formulaDetailPage");
  setActionStatus(`正在查看 ${formulaDisplayName(formula, index)} 的完整配方详情。`, "success");
}

function selectFormula(formula) {
  state.selectedFormula = formula;
  renderFormulaInspector(formula);
  const index = state.formulas.findIndex((item) => item.id === formula.id);
  if (document.getElementById("formulaDetailPage")?.classList.contains("active")) {
    renderFormulaDetailPage(formula, Math.max(0, index));
  }
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
  els.inspectorTitle.textContent = formulaDisplayName(formula, Math.max(0, rank - 1));
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
  const label = formula ? `当前配方 ${formulaDisplayName(formula)}` : "未选择配方";
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
  node.appendChild(renderFormulaEvidenceList(formula, true));
  return node;
}

function renderFormulaDetailPage(formula, index) {
  if (!formula) {
    els.formulaDetailPageTitle.textContent = "尚未选择配方";
    els.formulaDetailPageSummary.textContent = "从候选配方列表进入后查看完整明细、评分和证据链路。";
    els.formulaDetailPageRank.textContent = "未选择";
    els.formulaDetailHeroTitle.textContent = "选择配方后查看详情";
    els.formulaDetailHeroText.textContent = "完整配方信息会在这里展示。";
    els.formulaDetailPageScore.className = "score-ring";
    els.formulaDetailPageScore.setAttribute("style", "--score:0");
    els.formulaDetailPageScore.innerHTML = "<span>--</span>";
    els.formulaDetailPageBody.className = "formula-detail-page-body empty-state";
    els.formulaDetailPageBody.textContent = "选择一套候选方案后查看详情。";
    els.formulaDetailReviewPanel.className = "formula-detail-review-panel empty-state";
    els.formulaDetailReviewPanel.textContent = "选择一套候选方案后进行工程师审核。";
    return;
  }

  const displayName = formulaDisplayName(formula, index);
  const evidenceCount = (formula.evidence_ids || []).length;
  els.formulaDetailPageTitle.textContent = displayName;
  els.formulaDetailPageSummary.textContent = `综合评分 ${percent(formula.score?.overall)} · ${screeningLabel(formula.status)} · ${riskLabel(formula)} · ${evidenceCount} 条证据`;
  els.formulaDetailPageRank.textContent = `排名 #${index + 1}`;
  els.formulaDetailHeroTitle.textContent = displayName;
  els.formulaDetailHeroText.textContent = formula.recommendation_reason || "暂无推荐理由";
  const scoreNumber = Math.max(0, Math.min(100, Math.round(Number(formula.score?.overall || 0) * 100)));
  els.formulaDetailPageScore.className = "score-ring";
  els.formulaDetailPageScore.setAttribute("style", `--score:${scoreNumber}`);
  els.formulaDetailPageScore.innerHTML = `<span>${scoreNumber}%</span>`;
  els.formulaDetailPageBody.className = "formula-detail-page-body fade-in";
  els.formulaDetailPageBody.innerHTML = `
    <section class="formula-detail-section formula-detail-metrics" aria-label="配方评分维度">
      ${scoreEntries(formula).map(([label, value]) => `<div class="formula-detail-metric"><strong>${escapeHtml(label)}</strong><span>${percent(value)}</span><div class="score-bar" aria-hidden="true"><i style="width:${Math.max(0, Math.min(100, Math.round(Number(value || 0) * 100)))}%"></i></div></div>`).join("")}
    </section>
    <section class="formula-detail-section"><h3>配方明细</h3>${formulaTable(formula)}</section>
    <section class="formula-detail-section"><h3>推荐理由</h3><p>${escapeHtml(formula.recommendation_reason || "暂无推荐理由")}</p></section>
    <section class="formula-detail-section"><h3>风险提示</h3>${riskListHtml(formula)}</section>
    <section class="formula-detail-section"><h3>证据链路</h3><p>证据用于追溯推荐依据，不表示已完成实验验证。</p><div class="detail-evidence-list"></div></section>
  `;
  els.formulaDetailPageBody.querySelector(".detail-evidence-list")?.appendChild(renderFormulaEvidenceList(formula, true));

  renderFormulaDetailReviewPanel(formula);
}

function renderFormulaDetailReviewPanel(formula) {
  els.formulaDetailReviewPanel.className = "formula-detail-review-panel fade-in";
  els.formulaDetailReviewPanel.innerHTML = `
    <div class="detail-review-head">
      <p class="section-label">工程师审核</p>
      <h3>${escapeHtml(formulaDisplayName(formula))}</h3>
      <span>${escapeHtml(screeningLabel(formula.status))}</span>
    </div>
    <label for="detailEngineer">
      <span>工程师</span>
      <input id="detailEngineer" value="${escapeAttr(els.engineer.value)}" placeholder="请输入工程师姓名或工号">
    </label>
    <label for="detailDecision">
      <span>筛选决定</span>
      <select id="detailDecision">
        <option value="keep"${els.decision.value === "keep" ? " selected" : ""}>保留</option>
        <option value="modify"${els.decision.value === "modify" ? " selected" : ""}>要求修改</option>
        <option value="reject"${els.decision.value === "reject" ? " selected" : ""}>剔除</option>
      </select>
    </label>
    <label for="detailScreeningReason">
      <span>审核意见</span>
      <textarea id="detailScreeningReason" placeholder="请输入审核意见、实验关注点或修改依据">${escapeHtml(els.screeningReason.value)}</textarea>
    </label>
    <div class="detail-review-actions">
      <button class="ghost-danger" type="button" data-detail-decision="reject">剔除</button>
      <button class="secondary" type="button" data-detail-decision="modify">要求修改</button>
      <button class="primary" type="button" data-detail-submit>保留并进入实验</button>
    </div>
  `;
  bindFormulaDetailReviewActions();
}

function bindFormulaDetailReviewActions() {
  els.formulaDetailReviewPanel.querySelectorAll("[data-detail-decision]").forEach((button) => {
    button.addEventListener("click", () => {
      const decision = button.dataset.detailDecision;
      els.formulaDetailReviewPanel.querySelector("#detailDecision").value = decision;
      if (decision === "reject") els.formulaDetailReviewPanel.querySelector("#detailScreeningReason").value = "剔除：风险、证据或工程适配性不足，暂不进入实验。";
      if (decision === "modify") els.formulaDetailReviewPanel.querySelector("#detailScreeningReason").value = "要求修改：请调整原料比例或降低风险后重新评估。";
      submitFormulaDetailReview();
    });
  });
  els.formulaDetailReviewPanel.querySelector("[data-detail-submit]")?.addEventListener("click", submitFormulaDetailReview);
}

function submitFormulaDetailReview() {
  els.engineer.value = els.formulaDetailReviewPanel.querySelector("#detailEngineer")?.value || "";
  els.decision.value = els.formulaDetailReviewPanel.querySelector("#detailDecision")?.value || "keep";
  els.screeningReason.value = els.formulaDetailReviewPanel.querySelector("#detailScreeningReason")?.value || "";
  document.getElementById("submitScreening").click();
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

function renderFormulaEvidenceList(formula, detailed = false) {
  const evidenceIds = formula?.evidence_ids || [];
  const evidence = document.createElement("div");
  evidence.className = "evidence-list formula-evidence-list";
  if (!evidenceIds.length) {
    evidence.appendChild(emptyInline("暂无证据 ID"));
    return evidence;
  }
  const labelByEvidenceId = formulaEvidenceLabelMap(formula);
  evidenceIds.forEach((evidenceId) => {
    const label = labelByEvidenceId.get(evidenceId) || evidenceId;
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = detailed ? `${label} · 查看证据` : label;
    button.title = `${label}\n${evidenceId}`;
    button.setAttribute("aria-label", `查看证据 ${label}`);
    button.dataset.evidenceId = evidenceId;
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
  const rows = formulas.map((formula, index) => [`#${index + 1}`, formulaDisplayName(formula, index), percent(formula.score?.overall), strategyLabel(formula.strategy || "-"), ingredientDisplayNames(formula).join("、"), (formula.risk_notes || []).join("；") || "暂无风险提示", `${(formula.evidence_ids || []).length} 条`]);
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
  if (item.dataset.view) {
    setActiveView(item.dataset.view, { route: item.dataset.route });
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

function setActiveView(viewId, options = {}) {
  const activeViewId = document.getElementById(viewId) ? viewId : "workspaceCore";
  document.querySelectorAll(".app-view").forEach((view) => {
    view.classList.toggle("active", view.id === activeViewId);
  });
  syncRailActive(activeViewId);
  const route = options.route || viewRoutes[activeViewId] || viewRoutes.workspaceCore;
  if (canUseConsoleRoutes() && !options.skipHistory && window.location.pathname !== route) {
    if (options.replace) {
      history.replaceState({ viewId: activeViewId }, "", route);
    } else {
      history.pushState({ viewId: activeViewId }, "", route);
    }
  }
}

function syncRailActive(viewId) {
  document.querySelectorAll(".rail-item").forEach((button) => {
    button.classList.toggle("active", button.dataset.view === viewId);
  });
}

function viewForCurrentRoute() {
  if (!canUseConsoleRoutes()) {
    return "workspaceCore";
  }
  const path = window.location.pathname.replace(/\/$/, "");
  if (!path || path === "/console" || path === "/console/index.html") {
    return "workspaceCore";
  }
  return routeViews[path] || "workspaceCore";
}

function canUseConsoleRoutes() {
  return (window.location.protocol === "http:" || window.location.protocol === "https:")
    && window.location.pathname.startsWith("/console");
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
  const body = role === "assistant" && payload ? renderStructuredChatAnswer(text, payload) : `<p>${escapeHtml(text)}</p>`;
  node.innerHTML = `<strong>${role === "user" ? "配方师" : "AI"}</strong>${body}${meta}`;
  els.chatMessages.appendChild(node);
  node.querySelectorAll("[data-interactive-chat-graph]").forEach((target) => hydrateInteractiveChatGraph(target));
  els.chatMessages.scrollTop = els.chatMessages.scrollHeight;
}

function removePendingChatMessage() {
  els.chatMessages.querySelector('[data-pending="true"]')?.remove();
}

function renderStructuredChatAnswer(text, payload) {
  const rows = extractFormulaRows(payload, text);
  const graph = buildChatKnowledgeGraph(payload, rows);
  const sections = [`<p>${escapeHtml(text)}</p>`];
  if (rows.length) {
    sections.push(renderChatFormulaTable(rows));
    sections.push(renderChatFunctionGroups(rows));
  }
  if (graph.nodes.length > 1) {
    sections.push(renderChatRelationMap(graph));
    sections.push(renderChatCorePath(graph, payload));
  }
  return `<div class="structured-chat-answer">${sections.join("")}</div>`;
}

function extractFormulaRows(payload, text) {
  const labelById = knowledgeGraphLabelMap(payload);
  const structured = payload.formula_ingredients || payload.ingredients || payload.formula?.ingredients || payload.formulas?.[0]?.ingredients || [];
  if (Array.isArray(structured) && structured.length) {
    return structured.map((item) => ({
      name: displayIngredientName(item.name || item.ingredient_name, item.ingredient_id || item.id, labelById),
      concentration: item.concentration || item.percent || item.dosage || rangeText(item),
      functionGroup: item.function_group || item.function || item.category || item.role || "核心成分",
      role: item.core_effect || item.effect || item.reason || item.role || "-",
      id: item.ingredient_id || item.id || item.name || "",
    }));
  }
  const parsed = parseFormulaRowsFromText(text);
  if (parsed.length) return parsed.map((row) => ({ ...row, name: displayIngredientName(row.name, row.id, labelById) }));
  return knowledgeGraphRows(payload);
}

function parseFormulaRowsFromText(text) {
  const rows = [];
  const lines = String(text || "").split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
  for (const line of lines) {
    const cells = line.split("|").map((cell) => cell.trim()).filter(Boolean);
    if (cells.length >= 4 && !/^-+$/.test(cells.join("")) && !/成分/.test(cells[0])) {
      rows.push({ name: cells[0], concentration: cells[1], functionGroup: cells[2], role: cells.slice(3).join(" / "), id: cells[0] });
    }
  }
  return rows.slice(0, 12);
}

function buildChatKnowledgeGraph(payload, rows) {
  const fallback = buildFormulaRelationshipGraph(payload, rows);
  if (payload.knowledge_graph?.nodes?.length) {
    const graph = normalizeChatKnowledgeGraph(payload.knowledge_graph);
    if (graph.edges.length) return graph;
    return fallback.edges.length ? fallback : graph;
  }
  if (fallback.nodes.length > 1) return fallback;
  return { nodes: [], edges: [] };
}

function buildFormulaRelationshipGraph(payload, rows) {
  const center = {
    id: "formula-center",
    label: payload.title || "美白精华配方",
    group: "center",
  };
  const nodes = [center];
  const edges = [];
  const grouped = new Map();
  rows.forEach((row, index) => {
    const group = row.functionGroup || "核心成分";
    if (!grouped.has(group)) {
      const groupNode = { id: `group-${grouped.size}`, label: group, group: "function" };
      grouped.set(group, groupNode);
      nodes.push(groupNode);
      edges.push({ source: center.id, target: groupNode.id, label: "功效分类" });
    }
    const ingredientNode = {
      id: row.id || `ingredient-${index}`,
      label: row.name,
      group: "ingredient",
      concentration: row.concentration,
    };
    nodes.push(ingredientNode);
    edges.push({ source: grouped.get(group).id, target: ingredientNode.id, label: row.role || "证据关联" });
  });
  (payload.ingredient_ids || []).slice(0, 8).forEach((id) => {
    if (nodes.some((node) => node.id === id || node.label === id)) return;
    nodes.push({ id, label: id, group: "ingredient" });
  });
  (payload.relation_edges || []).slice(0, 12).forEach((edge) => {
    const source = String(edge.source || "");
    const target = String(edge.target || "");
    if (!source || !target) return;
    if (!nodes.some((node) => node.id === source)) nodes.push({ id: source, label: source, group: "function" });
    if (!nodes.some((node) => node.id === target)) nodes.push({ id: target, label: target, group: "ingredient" });
    edges.push({ source, target, label: edge.label || edge.type || "Yuxi 证据" });
  });
  return { nodes, edges };
}

function normalizeChatKnowledgeGraph(graph) {
  return {
    nodes: (graph.nodes || []).slice(0, 28).map((node, index) => ({
      id: String(node.id || `node-${index}`),
      label: node.label || node.name || node.id || `节点 ${index + 1}`,
      group: index === 0 ? "center" : node.type || node.group || "ingredient",
      description: node.description || "",
    })),
    edges: (graph.edges || []).slice(0, 48).map((edge, index) => ({
      source: String(edge.source || edge.source_id || ""),
      target: String(edge.target || edge.target_id || ""),
      label: edge.label || edge.type || edge.relation_type || `关系 ${index + 1}`,
    })).filter((edge) => edge.source && edge.target),
  };
}

function knowledgeGraphLabelMap(payload) {
  const map = new Map();
  (payload.knowledge_graph?.nodes || []).forEach((node) => {
    if (node.id && node.label) map.set(String(node.id), String(node.label));
  });
  return map;
}

function displayIngredientName(name, id, labelById) {
  const value = String(name || "").trim();
  if (value && !/^YUXI-[A-Z0-9-]+$/.test(value)) return value;
  const label = labelById.get(String(id || value));
  return label || value || String(id || "-");
}

function knowledgeGraphRows(payload) {
  return (payload.knowledge_graph?.nodes || []).slice(0, 8).map((node) => ({
    name: node.label || node.name || node.id,
    concentration: "-",
    functionGroup: node.type || "Yuxi 图谱",
    role: node.description || "图谱召回成分",
    id: node.id || node.label || "",
  }));
}

function renderChatFormulaTable(rows) {
  return `<section class="chat-answer-section"><h3>配方明细</h3><div class="chat-formula-table"><table><thead><tr><th>成分</th><th>浓度</th><th>功效分类</th><th>核心作用</th></tr></thead><tbody>${rows.map((row) => `<tr><td>${escapeHtml(row.name)}</td><td>${escapeHtml(row.concentration)}</td><td>${escapeHtml(row.functionGroup)}</td><td>${escapeHtml(row.role)}</td></tr>`).join("")}</tbody></table></div></section>`;
}

function renderChatFunctionGroups(rows) {
  const groups = new Map();
  rows.forEach((row) => {
    const group = row.functionGroup || "核心成分";
    if (!groups.has(group)) groups.set(group, []);
    groups.get(group).push(row);
  });
  return `<section class="chat-answer-section"><h3>成分功效关系</h3><div class="chat-function-graph">${Array.from(groups.entries()).map(([group, items], index) => `<div class="chat-function-row"><strong>${escapeHtml(group)}</strong><div>${items.map((item) => `<span class="function-chip chip-${index % 5}">${escapeHtml(item.name)}${item.concentration && item.concentration !== "-" ? ` (${escapeHtml(item.concentration)})` : ""}</span>`).join("")}</div></div>`).join("")}</div></section>`;
}

function renderChatRelationMap(graph) {
  const graphId = `chat-graph-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  return `<section class="chat-answer-section"><h3>知识图谱关系</h3><div class="chat-relation-map interactive-chat-graph" data-interactive-chat-graph="${escapeAttr(graphId)}" data-graph="${escapeAttr(JSON.stringify(graph))}">
    <div class="chat-graph-toolbar"><span>节点 ${graph.nodes.length} · 边 ${graph.edges.length}</span><button type="button" data-graph-fit>适配</button></div>
    <svg viewBox="0 0 760 320" role="img" aria-label="Yuxi 知识图谱关系"><g class="chat-graph-stage"><g class="chat-graph-edges"></g><g class="chat-graph-labels"></g><g class="chat-graph-nodes"></g></g></svg>
  </div></section>`;
}

function hydrateInteractiveChatGraph(root) {
  if (!root || root.dataset.hydrated === "true") return;
  root.dataset.hydrated = "true";
  let graph;
  try {
    graph = JSON.parse(root.dataset.graph || "{}");
  } catch (error) {
    root.classList.add("empty-state");
    root.textContent = "图谱数据解析失败。";
    return;
  }
  const svg = root.querySelector("svg");
  const stage = root.querySelector(".chat-graph-stage");
  const edgeLayer = root.querySelector(".chat-graph-edges");
  const labelLayer = root.querySelector(".chat-graph-labels");
  const nodeLayer = root.querySelector(".chat-graph-nodes");
  if (!svg || !stage || !edgeLayer || !labelLayer || !nodeLayer) return;

  const width = 760;
  const height = 320;
  const nodes = forceLayoutNodes(graph.nodes || [], graph.edges || [], width, height);
  const edges = (graph.edges || []).filter((edge) => nodes.some((node) => node.id === edge.source) && nodes.some((node) => node.id === edge.target));
  const byId = new Map(nodes.map((node) => [node.id, node]));
  let transform = { x: 0, y: 0, scale: 1 };
  let activeNode = null;
  let activePan = null;
  let lastPointer = null;

  function render() {
    stage.setAttribute("transform", `translate(${transform.x} ${transform.y}) scale(${transform.scale})`);
    edgeLayer.innerHTML = edges.map((edge, index) => {
      const source = byId.get(edge.source);
      const target = byId.get(edge.target);
      return `<line class="chat-graph-edge" data-source="${escapeAttr(edge.source)}" data-target="${escapeAttr(edge.target)}" style="--edge-index:${index}" x1="${source.x}" y1="${source.y}" x2="${target.x}" y2="${target.y}"></line>`;
    }).join("");
    labelLayer.innerHTML = edges.map((edge) => {
      const source = byId.get(edge.source);
      const target = byId.get(edge.target);
      return `<text class="chat-graph-edge-label" x="${(source.x + target.x) / 2}" y="${(source.y + target.y) / 2 - 6}">${escapeHtml(summaryText(edge.label, 10))}</text>`;
    }).join("");
    nodeLayer.innerHTML = nodes.map((node, index) => {
      const radius = node.group === "center" ? 28 : node.group === "function" ? 18 : 15;
      return `<g class="chat-graph-node ${chatGraphNodeClass(node)}" data-node-id="${escapeAttr(node.id)}" tabindex="0" role="button" aria-label="${escapeAttr(node.label)}" style="--node-index:${index}" transform="translate(${node.x} ${node.y})">
        <circle r="${radius}"></circle>
        <text y="${radius + 18}">${escapeHtml(summaryText(node.label, node.group === "center" ? 16 : 14))}</text>
        <title>${escapeHtml(node.label)}</title>
      </g>`;
    }).join("");
    bindGraphNodeEvents();
  }

  function updatePositions() {
    edgeLayer.querySelectorAll("line").forEach((line) => {
      const source = byId.get(line.dataset.source);
      const target = byId.get(line.dataset.target);
      if (!source || !target) return;
      line.setAttribute("x1", source.x);
      line.setAttribute("y1", source.y);
      line.setAttribute("x2", target.x);
      line.setAttribute("y2", target.y);
    });
    labelLayer.querySelectorAll("text").forEach((label, index) => {
      const edge = edges[index];
      const source = byId.get(edge.source);
      const target = byId.get(edge.target);
      label.setAttribute("x", (source.x + target.x) / 2);
      label.setAttribute("y", (source.y + target.y) / 2 - 6);
    });
    nodeLayer.querySelectorAll("[data-node-id]").forEach((nodeEl) => {
      const node = byId.get(nodeEl.dataset.nodeId);
      if (node) nodeEl.setAttribute("transform", `translate(${node.x} ${node.y})`);
    });
  }

  function bindGraphNodeEvents() {
    nodeLayer.querySelectorAll("[data-node-id]").forEach((nodeEl) => {
      nodeEl.addEventListener("pointerdown", (event) => {
        event.preventDefault();
        activeNode = byId.get(nodeEl.dataset.nodeId);
        lastPointer = pointerPoint(event, svg);
        nodeEl.setPointerCapture(event.pointerId);
        highlightChatGraphNode(root, activeNode?.id, edges);
      });
      nodeEl.addEventListener("click", () => highlightChatGraphNode(root, nodeEl.dataset.nodeId, edges));
      nodeEl.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") highlightChatGraphNode(root, nodeEl.dataset.nodeId, edges);
      });
    });
  }

  svg.addEventListener("pointerdown", (event) => {
    if (event.target.closest?.("[data-node-id]")) return;
    activePan = pointerPoint(event, svg);
    svg.setPointerCapture(event.pointerId);
  });
  svg.addEventListener("pointermove", (event) => {
    const current = pointerPoint(event, svg);
    if (activeNode && lastPointer) {
      activeNode.x += (current.x - lastPointer.x) / transform.scale;
      activeNode.y += (current.y - lastPointer.y) / transform.scale;
      lastPointer = current;
      updatePositions();
      return;
    }
    if (activePan) {
      transform.x += current.x - activePan.x;
      transform.y += current.y - activePan.y;
      activePan = current;
      stage.setAttribute("transform", `translate(${transform.x} ${transform.y}) scale(${transform.scale})`);
    }
  });
  svg.addEventListener("pointerup", () => {
    activeNode = null;
    activePan = null;
    lastPointer = null;
  });
  svg.addEventListener("pointerleave", () => {
    activeNode = null;
    activePan = null;
    lastPointer = null;
  });
  svg.addEventListener("wheel", (event) => {
    event.preventDefault();
    const direction = event.deltaY > 0 ? 0.9 : 1.1;
    transform.scale = Math.max(0.55, Math.min(2.2, transform.scale * direction));
    stage.setAttribute("transform", `translate(${transform.x} ${transform.y}) scale(${transform.scale})`);
  }, { passive: false });
  root.querySelector("[data-graph-fit]")?.addEventListener("click", () => {
    transform = { x: 0, y: 0, scale: 1 };
    stage.setAttribute("transform", "translate(0 0) scale(1)");
  });
  render();
}

function forceLayoutNodes(nodes, edges, width, height) {
  const centerX = width / 2;
  const centerY = height / 2;
  const normalized = nodes.slice(0, 32).map((node, index) => {
    const angle = (index / Math.max(1, nodes.length)) * Math.PI * 2 - Math.PI / 2;
    const isCenter = index === 0 || node.group === "center";
    const radius = isCenter ? 0 : 92 + (index % 4) * 26;
    return {
      id: String(node.id || `node-${index}`),
      label: node.label || node.name || node.id || `节点 ${index + 1}`,
      group: isCenter ? "center" : node.group || node.type || "ingredient",
      x: centerX + Math.cos(angle) * radius,
      y: centerY + Math.sin(angle) * radius,
    };
  });
  const byId = new Map(normalized.map((node) => [node.id, node]));
  const links = edges.map((edge) => ({ source: byId.get(edge.source), target: byId.get(edge.target) })).filter((edge) => edge.source && edge.target);
  for (let tick = 0; tick < 90; tick += 1) {
    for (let i = 0; i < normalized.length; i += 1) {
      for (let j = i + 1; j < normalized.length; j += 1) {
        const a = normalized[i];
        const b = normalized[j];
        const dx = a.x - b.x || 0.1;
        const dy = a.y - b.y || 0.1;
        const distance = Math.max(24, Math.hypot(dx, dy));
        const force = 520 / (distance * distance);
        if (a.group !== "center") {
          a.x += (dx / distance) * force;
          a.y += (dy / distance) * force;
        }
        if (b.group !== "center") {
          b.x -= (dx / distance) * force;
          b.y -= (dy / distance) * force;
        }
      }
    }
    links.forEach((link) => {
      const dx = link.target.x - link.source.x;
      const dy = link.target.y - link.source.y;
      const distance = Math.max(1, Math.hypot(dx, dy));
      const desired = link.source.group === "center" || link.target.group === "center" ? 96 : 118;
      const force = (distance - desired) * 0.018;
      if (link.source.group !== "center") {
        link.source.x += (dx / distance) * force;
        link.source.y += (dy / distance) * force;
      }
      if (link.target.group !== "center") {
        link.target.x -= (dx / distance) * force;
        link.target.y -= (dy / distance) * force;
      }
    });
    normalized.forEach((node) => {
      if (node.group === "center") {
        node.x = centerX;
        node.y = centerY;
      } else {
        node.x = Math.max(54, Math.min(width - 54, node.x + (centerX - node.x) * 0.006));
        node.y = Math.max(44, Math.min(height - 44, node.y + (centerY - node.y) * 0.006));
      }
    });
  }
  return normalized;
}

function pointerPoint(event, svg) {
  const rect = svg.getBoundingClientRect();
  return {
    x: ((event.clientX - rect.left) / Math.max(1, rect.width)) * 760,
    y: ((event.clientY - rect.top) / Math.max(1, rect.height)) * 320,
  };
}

function highlightChatGraphNode(root, nodeId, edges) {
  const related = new Set([nodeId]);
  edges.forEach((edge) => {
    if (edge.source === nodeId) related.add(edge.target);
    if (edge.target === nodeId) related.add(edge.source);
  });
  root.querySelectorAll("[data-node-id]").forEach((node) => {
    node.classList.toggle("selected", node.dataset.nodeId === nodeId);
    node.classList.toggle("dimmed", !related.has(node.dataset.nodeId));
  });
  root.querySelectorAll(".chat-graph-edge").forEach((edge) => {
    const active = edge.dataset.source === nodeId || edge.dataset.target === nodeId;
    edge.classList.toggle("selected", active);
    edge.classList.toggle("dimmed", !active);
  });
}

function chatGraphNodeClass(node) {
  const value = String(node?.group || "").toLowerCase();
  if (value.includes("center")) return "center";
  if (value.includes("function") || value.includes("effect") || value.includes("功效")) return "function";
  return "ingredient";
}

function renderChatCorePath(graph, payload) {
  const paths = (payload.core_path || []).length ? payload.core_path : graph.edges.slice(0, 4).map((edge, index) => `${index + 1}. ${edge.label}：${edge.source} → ${edge.target}`);
  return `<section class="chat-answer-section"><h3>核心链路</h3><ol class="chat-core-path">${paths.map((path) => `<li>${escapeHtml(path)}</li>`).join("")}</ol></section>`;
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
  return `<div class="ingredient-compact">${ingredients.map((item) => {
    const name = ingredientDisplayName(item);
    const identity = item.ingredient_id || name;
    return `<div class="ingredient-row"><span title="${escapeAttr(identity)}">${escapeHtml(name)}</span><span>${escapeHtml(rangeText(item))}</span></div>`;
  }).join("")}</div>`;
}

function renderScoreRing(value) {
  const number = Math.max(0, Math.min(100, Math.round(Number(value || 0) * 100)));
  return `<div class="score-ring" style="--score:${number}"><span>${number}%</span></div>`;
}

function formulaTable(formula) {
  const rows = (formula.ingredients || []).map((item) => {
    const name = ingredientDisplayName(item);
    const ingredientId = String(item.ingredient_id || "");
    const evidence = evidenceIdsForIngredient(item);
    return `<article class="formula-detail-row">
      <div class="formula-ingredient-main">
        <strong title="${escapeAttr(ingredientId || name)}">${escapeHtml(name)}</strong>
      </div>
      <span class="formula-role">${escapeHtml(item.role || "-")}</span>
      <span class="formula-range">${escapeHtml(rangeText(item))}</span>
      <div class="formula-evidence-refs" aria-label="对应 Yuxi 证据">
        ${evidence.length ? evidence.map((id) => `<span title="${escapeAttr(id)}">${escapeHtml(compactEvidenceId(id))}</span>`).join("") : "<span>-</span>"}
      </div>
    </article>`;
  }).join("");
  return `<div class="formula-detail-list"><div class="formula-detail-head"><span>原料简称</span><span>角色</span><span>比例</span></div>${rows}</div>`;
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

function ingredientDisplayNames(formula) {
  return (formula.ingredients || []).map((item) => ingredientDisplayName(item));
}

function ingredientEvidenceText(item) {
  const ids = evidenceIdsForIngredient(item);
  if (!ids.length) return "-";
  return ids.map((id) => `${ingredientDisplayName(item)}（${id}）`).join("；");
}

function formulaEvidenceLabelMap(formula) {
  const map = new Map();
  (formula?.ingredients || []).forEach((ingredient) => {
    evidenceIdsForIngredient(ingredient).forEach((evidenceId) => {
      map.set(evidenceId, ingredientDisplayName(ingredient));
    });
  });
  return map;
}

function evidenceIdsForIngredient(item) {
  if (Array.isArray(item?.evidence_ids) && item.evidence_ids.length) {
    return item.evidence_ids;
  }
  const ingredientId = String(item?.ingredient_id || "");
  if (ingredientId.startsWith("YUXI-")) {
    return [`YUXI-GRAPH-${ingredientId.slice("YUXI-".length)}`];
  }
  return [];
}

function compactYuxiId(value) {
  const id = String(value || "").trim();
  if (!id) return "";
  if (id.length <= 18) return id;
  const prefix = id.startsWith("YUXI-") ? "YUXI" : id.slice(0, 4);
  return `${prefix}-…${id.slice(-8)}`;
}

function compactEvidenceId(value) {
  const id = String(value || "").trim();
  if (!id) return "";
  if (id.length <= 18) return id;
  if (id.startsWith("YUXI-GRAPH-")) return `GRAPH-…${id.slice(-8)}`;
  return `${id.slice(0, 6)}…${id.slice(-8)}`;
}

function ingredientDisplayName(item) {
  const ingredientId = normalizeYuxiPublicId(item?.ingredient_id) || String(item?.ingredient_id || "").trim();
  const candidates = [
    ingredientNameByYuxiId[ingredientId],
    item?.name,
    item?.ingredient_name,
    item?.display_name,
    item?.name_en,
    item?.inci_name,
    item?.name_cn,
  ];
  const readable = candidates.map((value) => String(value || "").trim()).find((value) => value && !isYuxiInternalId(value));
  return readable || compactYuxiId(ingredientId) || "-";
}

function formulaDisplayName(formula, index = 0) {
  const explicit = formula?.name || formula?.title || formula?.formula_name || formula?.display_name;
  if (explicit && !isYuxiInternalId(String(explicit))) {
    return String(explicit);
  }
  const goal = formula?.goal || els.goal?.value?.trim() || "功效";
  const form = formula?.dosage_form || els.dosageForm?.value?.trim() || "配方";
  const topIngredient = (formula?.ingredients || [])
    .map((item) => ingredientDisplayName(item))
    .filter(Boolean)
    .slice(0, 2)
    .join(" + ");
  const prefix = topIngredient && !isYuxiInternalId(topIngredient) ? `${topIngredient} ` : "";
  return `${prefix}${goal}${form}方案 ${index + 1}`;
}

function isYuxiInternalId(value) {
  return /^YUXI-[A-Z0-9-]+$/.test(String(value || "").trim());
}

function normalizeYuxiPublicId(value) {
  const raw = String(value || "").trim();
  if (!raw) return "";
  if (!/^YUXI-/i.test(raw) && !/^[a-f0-9]{32}$/i.test(raw)) return "";
  const body = raw.replace(/^YUXI-/i, "").toUpperCase();
  if (!/^[A-Z0-9-]+$/.test(body)) return "";
  return `YUXI-${body}`;
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
