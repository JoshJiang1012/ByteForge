(() => {
  "use strict";

  const TOTAL = 100;
  const NORMAL_TOTAL = 90;
  const BOSS_IDS = [10,20,30,40,50,60,70,80,90,100];
  const TRACKS = ["Core","Identity","Host","Web","Network","Secrets","Detection","IR","SecureCode","Purple"];
  const SECTORS = [
    { start:1, end:10, en:"Core Security Automation", zh:"資安自動化基礎" },
    { start:11, end:20, en:"Identity & Access Control", zh:"身分與存取控制" },
    { start:21, end:30, en:"Linux & Host Hardening", zh:"Linux 與主機強化" },
    { start:31, end:40, en:"Web Request Security", zh:"Web 請求安全" },
    { start:41, end:50, en:"Network & Firewall", zh:"網路與防火牆" },
    { start:51, end:60, en:"Secrets & Crypto Hygiene", zh:"秘密與密碼學衛生" },
    { start:61, end:70, en:"Detection Engineering", zh:"偵測工程" },
    { start:71, end:80, en:"Incident Response & Forensics", zh:"事件應變與鑑識" },
    { start:81, end:90, en:"Secure Coding", zh:"安全程式設計" },
    { start:91, end:100, en:"Purple-Team Integrated Range", zh:"Purple Team 綜合攻防" },
  ];
  const STORE = { progress:"byteforge-cyber-progress-v5", drafts:"byteforge-cyber-code-v5", selected:"byteforge-cyber-selected-v5", lang:"byteforge-language-v1", perf:"byteforge-performance-v5" };
  const LEGACY = { progress:"byteforge-cyber-progress-v5", drafts:"byteforge-cyber-code-v5", selected:"byteforge-cyber-selected-v5" };

  const I18N = {
    en: {
      bootConnecting:"Connecting to local Cyber Range…", performanceMode:"Performance Mode", worldTitle:"White-Hat Cyber Range", continuousRule:"The next mission unlocks immediately after the previous clear. No daily limit.",
      labsCleared:"Non-boss missions", bossesDefeated:"Boss protocols", rangeRuleTitle:"RANGE RULE", rangeRuleBody:"Every mission uses supplied synthetic data only. The Judge blocks imports, file access, and network access.",
      jumpToEditor:"Write code now →", goal:"GOAL", missionContract:"MISSION CONTRACT", functionLabel:"Function", testsLabel:"Tests", conceptLabel:"Core", clearObjectives:"CLEAR OBJECTIVES", visibleChecks:"VISIBLE CHECKS",
      hintSystem:"HINT SYSTEM", hintPolicy:"Hints go from direction → structure → near-solution.", editorShortcut:"Ctrl + Enter run · Tab indent", resetCode:"Reset code", sandboxLabel:"LOCAL PYTHON CYBER SANDBOX · import / file / network disabled", runTests:"Run tests",
      judgeOutput:"JUDGE OUTPUT", upcomingEncounter:"UPCOMING ENCOUNTER", liveTutor:"LIVE TUTOR", syntax:"SYNTAX", whyItMatters:"WHY IT MATTERS", missionRecipe:"MISSION RECIPE", needFix:"Need a fix?", askPatch:"Ask Patch for the next hint", skillTree:"SKILL TREE", resetProgress:"Reset all local progress",
      ready:"READY", running:"RUNNING…", executing:"EXECUTING", terminalEmpty:"$ Write your solution, then press Ctrl + Enter.", startingJudge:"$ Starting isolated local Judge…", offline:"OFFLINE", allPass:"ALL TESTS PASS", testsFailed:"TESTS FAILED", programOutput:"PROGRAM OUTPUT", pass:"PASS", fail:"FAIL", hiddenTest:"Hidden test", expected:"expected", actual:"actual", hiddenPassed:"Hidden condition satisfied.", hiddenFailed:"A hidden edge case failed.",
      previousRequired:"Clear the previous mission first.", missionClear:(xp,already)=>already?"PRACTICE RUN COMPLETE · MISSION ALREADY CLEARED":`MISSION CLEAR · +${xp} XP · NEXT MISSION UNLOCKED`, finalVictory:"CYBER FORTRESS SECURED · ALL 100 MISSIONS COMPLETE", clearToast:(id,xp)=>`Mission ${String(id).padStart(2,"0")} cleared · +${xp} XP`,
      resetCodeConfirm:"Reset this mission to its starter template?", resetAllConfirm:"Reset all ByteForge 5.0 progress and drafts in this browser?", progressReset:"Local progress reset.", showHint:n=>`Show hint ${n}`, allHints:"All hints revealed", hintLabels:["DIRECTION","STRUCTURE","NEAR SOLUTION"],
      judgeOnline:(py,q)=>`judge online · Python ${py} · ${q} missions`, bootError:e=>`boot failed · ${e}`, bootHelp:"Keep the ByteForge launcher terminal open and use the exact URL it prints.", testsSummary:(total,hidden)=>`${total} tests · ${hidden} hidden`, visibleExpected:value=>`→ ${value}`,
      bossPreview:remaining=>remaining===0?"Warden Null is waiting in this mission.":`${remaining} mission${remaining===1?"":"s"} until the next boss protocol.`, bossLine:"Warden Null controls ten sector protocols. Every 10th mission is a boss encounter.",
      lyraDefault:"Read the contract first. Then learn only the syntax this mission introduces.", patchDefault:"Run your code first. If something fails, I’ll point to the next thing to inspect.", patchSyntax:"The Judge found a syntax problem. Check the reported line, then compare indentation and punctuation with Lyra’s example.", patchBlocked:"The sandbox blocked a system capability. This mission can be solved with pure Python and supplied data—no imports or device access are needed.", patchFail:"Your program ran, so the syntax is valid. Compare the visible expected value with your actual value and inspect the first rule that can produce that difference.", patchPass:"Nice. The visible and hidden checks agree with your logic. You can continue immediately.",
      trackLabels:{Core:"Core Security Automation",Identity:"Identity & Access",Host:"Host Hardening",Web:"Web Security",Network:"Network & Firewall",Secrets:"Secrets & Crypto",Detection:"Detection Engineering",IR:"Incident Response",SecureCode:"Secure Coding",Purple:"Purple Team"}
    },
    "zh-Hant": {
      bootConnecting:"正在連線到本機 Cyber Range…", performanceMode:"效能模式", worldTitle:"白帽資安 Cyber Range", continuousRule:"前一關通過後下一關立即解鎖，沒有每日限制。",
      labsCleared:"一般攻防關卡", bossesDefeated:"Boss Protocol", rangeRuleTitle:"RANGE 規則", rangeRuleBody:"所有任務只處理題目提供的模擬資料；Judge 已封鎖 import、檔案與網路存取。",
      jumpToEditor:"直接寫程式 →", goal:"這關到底要做什麼", missionContract:"任務規格", functionLabel:"要完成的函式", testsLabel:"測試", conceptLabel:"本關核心", clearObjectives:"明確任務目標", visibleChecks:"你現在就能看到的測試",
      hintSystem:"提示系統", hintPolicy:"提示依序是：方向 → 程式結構 → 接近解法。", editorShortcut:"Ctrl + Enter 執行 · Tab 縮排", resetCode:"重設程式", sandboxLabel:"LOCAL PYTHON CYBER SANDBOX · 已停用 import / 檔案 / 網路", runTests:"執行測試",
      judgeOutput:"JUDGE 輸出", upcomingEncounter:"即將遭遇", liveTutor:"即時老師", syntax:"這關要學的語法", whyItMatters:"為什麼資安會用到", missionRecipe:"照這個順序寫", needFix:"需要幫忙？", askPatch:"請 Patch 給下一個提示", skillTree:"技能樹", resetProgress:"重設所有本機進度",
      ready:"READY", running:"執行中…", executing:"EXECUTING", terminalEmpty:"$ 寫完程式後按 Ctrl + Enter 執行。", startingJudge:"$ 啟動隔離式本機 Judge…", offline:"OFFLINE", allPass:"所有測試通過", testsFailed:"測試失敗", programOutput:"程式輸出", pass:"通過", fail:"失敗", hiddenTest:"隱藏測試", expected:"預期", actual:"實際", hiddenPassed:"隱藏邊界條件通過。", hiddenFailed:"有一個隱藏邊界條件沒有通過。",
      previousRequired:"請先通過前一關，下一關才會立刻解鎖。", missionClear:(xp,already)=>already?"這關已通關 · 本次為練習執行":`任務完成 · +${xp} XP · 下一關已立即解鎖`, finalVictory:"CYBER FORTRESS SECURED · 100 關全部完成", clearToast:(id,xp)=>`第 ${id} 關通過 · +${xp} XP`,
      resetCodeConfirm:"要把這關程式重設成最初模板嗎？", resetAllConfirm:"要重設此瀏覽器中的 ByteForge 5.0 進度與草稿嗎？", progressReset:"已重設本機進度。", showHint:n=>`顯示提示 ${n}`, allHints:"全部提示已顯示", hintLabels:["方向","程式結構","接近解法"],
      judgeOnline:(py,q)=>`Judge 已連線 · Python ${py} · ${q} 關`, bootError:e=>`啟動失敗 · ${e}`, bootHelp:"請保持 ByteForge 啟動器終端機開啟，並使用它顯示的實際網址。", testsSummary:(total,hidden)=>`${total} 組測試 · ${hidden} 組隱藏`, visibleExpected:value=>`→ ${value}`,
      bossPreview:remaining=>remaining===0?"Warden Null 就在這一關等你。":`距離下一個 Boss Protocol 還有 ${remaining} 關。`, bossLine:"Warden Null 控制十個 Sector Protocol；每第 10 關就是一次 Boss 遭遇。",
      lyraDefault:"先讀任務規格，再只學這一關新增的語法。", patchDefault:"先執行一次。如果失敗，我會告訴你下一個最該檢查的地方。", patchSyntax:"Judge 找到語法錯誤。先看它指出的行數，再拿你的縮排與標點和 Lyra 右側範例逐字比較。", patchBlocked:"Sandbox 阻擋了系統能力。這一關只需要純 Python 與題目提供的資料，不需要 import、檔案或裝置存取。", patchFail:"程式已經能執行，所以不是 Python 語法問題。先比較畫面上的「預期」與「實際」，再找第一個可能造成差異的判斷式。", patchPass:"很好。公開測試與隱藏測試都同意你的邏輯，可以立刻繼續下一關。",
      trackLabels:{Core:"資安自動化",Identity:"身分與存取",Host:"主機強化",Web:"Web 安全",Network:"網路與防火牆",Secrets:"秘密與密碼學",Detection:"偵測工程",IR:"事件應變",SecureCode:"安全程式設計",Purple:"Purple Team"}
    }
  };

  let quests = [], selectedId = 1, progress = {completed:[],xp:0,noHintClears:[],hintsUsed:{}}, drafts = {}, lang="zh-Hant", openSectors=new Set([1]), runningJudge=false, draftTimer=0, highlightFrame=0, lastLineCount=0, lastJudge=null;
  const els = {};
  const ids = ["boot","boot-status","app","performance-toggle","lang-zh","lang-en","player-level","quest-counter","world-percent","world-meter","sector-nav","labs-value","boss-value","xp-current","mission-panel","mission-number","mission-track","mission-mode","mission-difficulty","mission-xp","jump-editor","mission-title","mission-subtitle","boss-badge","mission-brief","contract-function","contract-tests","mission-concept","objective-state","mission-objectives","visible-check-count","visible-tests","hint-button","hint-list","coding-panel","file-name","editor-symbol","reset-code","line-numbers","editor-stage","active-line","highlight-layer","highlight-code","code-editor","typing-pop","cursor-position","run-button","terminal","judge-state","terminal-content","lyra-line","syntax-title","syntax-body","syntax-example","syntax-why","syntax-steps","boss-preview","boss-preview-text","boss-distance","skill-tree","reset-progress","boss-presence","patch-launcher","patch-assist","patch-close","patch-message","ask-patch","toast"];
  function cacheElements(){ ids.forEach(id=>els[id]=document.getElementById(id)); }
  function t(key,...args){ const v=(I18N[lang]&&I18N[lang][key]) ?? I18N.en[key] ?? key; return typeof v==="function"?v(...args):v; }
  function applyTranslations(){ document.documentElement.lang=lang; document.querySelectorAll("[data-i18n]").forEach(el=>{ const key=el.dataset.i18n; if(I18N[lang]?.[key]!==undefined) el.textContent=t(key); }); els["lang-zh"].classList.toggle("active",lang==="zh-Hant"); els["lang-en"].classList.toggle("active",lang==="en"); }
  function setLanguage(next){ lang=next; localStorage.setItem(STORE.lang,lang); applyTranslations(); renderAll(); }
  function setPerformance(on){ document.body.dataset.performance=on?"on":"off"; els["performance-toggle"].checked=on; localStorage.setItem(STORE.perf,on?"on":"off"); }
  function escapeHtml(value){ return String(value).replace(/[&<>"']/g,ch=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch])); }
  function levelFromXp(xp){ return Math.max(1,Math.floor(Math.sqrt(Math.max(0,xp)/160))+1); }
  function isComplete(id){ return progress.completed.includes(id); }
  function canOpen(id){ return id===1 || isComplete(id) || isComplete(id-1); }
  function currentQuest(){ return quests.find(q=>q.id===selectedId)||quests[0]; }
  function localizedQuest(q){ if(lang==="en") return q; const z=q?.i18n?.["zh-Hant"]||{}; return {...q,...z,syntax:{...q.syntax,...(z.syntax||{})}}; }
  function saveProgress(){ localStorage.setItem(STORE.progress,JSON.stringify(progress)); }
  function saveDrafts(){ localStorage.setItem(STORE.drafts,JSON.stringify(drafts)); }
  function parseJson(raw,fallback){ try{return JSON.parse(raw)||fallback;}catch{return fallback;} }
  function loadState(){ lang=localStorage.getItem(STORE.lang)||"zh-Hant"; if(!I18N[lang])lang="zh-Hant"; const storedProgress=localStorage.getItem(STORE.progress); const storedDrafts=localStorage.getItem(STORE.drafts); const storedSelected=localStorage.getItem(STORE.selected); progress=parseJson(storedProgress,{completed:[],xp:0,noHintClears:[],hintsUsed:{}}); drafts=parseJson(storedDrafts,{}); selectedId=Math.max(1,Math.min(TOTAL,Number(storedSelected)||1)); if(!canOpen(selectedId))selectedId=Math.min(TOTAL,(progress.completed.at(-1)||0)+1); }

  // ... ByteForge 5.0 UI runtime ...
  async function boot(){cacheElements();applyTranslations();setPerformance(localStorage.getItem(STORE.perf)!=="off");try{const health=await fetch("/api/health",{cache:"no-store"});if(!health.ok)throw new Error(`health HTTP ${health.status}`);const h=await health.json();els["boot-status"].textContent=t("judgeOnline",h.python,h.quests);const response=await fetch("/api/quests",{cache:"no-store"});if(!response.ok)throw new Error(`quests HTTP ${response.status}`);const payload=await response.json();quests=payload.quests;if(!Array.isArray(quests)||quests.length!==TOTAL||quests.filter(q=>q.boss).length!==10)throw new Error("quest catalog incomplete");loadState();document.querySelectorAll("[data-i18n]").forEach(el=>{const key=el.dataset.i18n;if(I18N[lang]?.[key]!==undefined)el.textContent=t(key);});els.boot.hidden=true;els.app.hidden=false;}catch(err){els["boot-status"].textContent=t("bootError",err.message);document.querySelector(".boot-card p").textContent=t("bootHelp");}}
  document.addEventListener("DOMContentLoaded",boot);
})();
