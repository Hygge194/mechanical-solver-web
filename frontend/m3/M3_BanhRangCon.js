/**
 * ============================================================
 *  M3_BanhRangCon.js  —  Controller của Module 3
 *  Bộ truyền bánh răng côn – Răng thẳng
 * ============================================================
 *
 *  Kiến trúc phụ thuộc:
 *    storage.js   → loadData(key) / saveData(key, obj)
 *    formulas.js  → calculate(params) và các hàm tính cơ khí
 *    workflow.js  → goToModule(moduleId)
 *
 *  File này KHÔNG chứa:
 *    - Công thức cơ khí dài
 *    - CSS / HTML string
 *
 *  File này CHỈ làm:
 *    - Điều phối luồng dữ liệu giữa UI, formulas.js và storage.js
 * ============================================================
 */

// ─────────────────────────────────────────────────────────────
// CONSTANTS
// ─────────────────────────────────────────────────────────────

/** Key dùng để đọc / ghi localStorage (hoặc bất kỳ storage nào) */
const M2_KEY = 'M2_Data';
const M3_KEY = 'M3_Data';

/** Mapping id HTML → key object params */
const INPUT_MAP = {
  inT1:    'T1',
  inN1:    'n1',
  inU:     'u',
  inTh:    't_h',
  inKqt:   'K_qt',
  inKbe:   'K_be',
  inHB1:   'HB1',
  inHB2:   'HB2',
  inSigB1: 'sigB1',
  inSigB2: 'sigB2',
  inSigCh1:'sigCh1',
  inSigCh2:'sigCh2',
  inKFC:   'K_FC',
};

/** Danh sách id cần reset về "—" sau khi reset form */
const RESULT_IDS = [
  'rSHL1','rSHL2','rSFL1','rSFL2',
  'rNHO1','rNHO2','rKHL1','rKHL2',
  'rSHCP1','rSHCP2','rSHCPdung','rSFCP1','rSFCP2',
  'ckV','ckSH','ckSF1','ckSF2',
  'ckSHmax','ckSF1max','ckSF2max',
  'hKHb','hKFb','hKHv','hKFv',
  'hKH','hKF','hZH','hEps',
  'hZe','hYe','hYF1','hYF2',
];

const CHECK_IDS = [
  'ckVs','ckSHs','ckSF1s','ckSF2s',
  'ckSHmaxs','ckSF1maxs','ckSF2maxs',
];

const STEP_COUNT = 6;


// ─────────────────────────────────────────────────────────────
// 1. LOAD DATA  –  Đọc dữ liệu từ M2
// ─────────────────────────────────────────────────────────────

/**
 * Đọc M2_Data từ storage và trả về object.
 * Nếu không có dữ liệu, trả về null (caller xử lý).
 *
 * @returns {Object|null}
 */
function loadM2Data() {
  try {
    const raw = (typeof loadData === 'function')
      ? loadData(M2_KEY)
      : JSON.parse(localStorage.getItem(M2_KEY) || 'null');

    if (!raw) {
      console.warn('[M3] Không tìm thấy M2_Data. Dùng giá trị mặc định.');
    }
    return raw;
  } catch (err) {
    console.error('[M3] Lỗi đọc M2_Data:', err);
    return null;
  }
}


// ─────────────────────────────────────────────────────────────
// 2. INIT UI  –  Khởi tạo giao diện
// ─────────────────────────────────────────────────────────────

/**
 * Điền dữ liệu từ M2 vào các ô input tương ứng.
 * Nếu M2 không có giá trị, giữ nguyên placeholder mặc định trong HTML.
 *
 * @param {Object|null} m2
 */
function initUI(m2) {
  // Cập nhật đồng hồ topbar
  const tbDate = document.getElementById('tbDate');
  if (tbDate) {
    tbDate.textContent = new Date().toLocaleDateString('vi-VN', {
      weekday: 'short', day: '2-digit', month: '2-digit', year: 'numeric',
    });
  }

  if (!m2) return; // Không có M2 → giữ nguyên giá trị mặc định

  // Ánh xạ trường M2 → ô input M3
  const m2ToInput = {
    P2: null,    // Công suất – dùng để tính T1 nếu chưa có
    n2: 'inN1',  // Tốc độ trục vào M3 = n2 của M2
    i_dai: null, // Tỉ số truyền đai – đã dùng xong
    T2: 'inT1',  // Mô men xoắn trục ra M2 = trục vào M3
    u_hop: 'inU',// Tỉ số truyền bánh răng côn (nếu M2 truyền sang)
    t_h: 'inTh', // Thời gian làm việc từ M1/M2
  };

  Object.entries(m2ToInput).forEach(([m2Key, inputId]) => {
    if (!inputId) return;
    const el = document.getElementById(inputId);
    if (el && m2[m2Key] !== undefined && m2[m2Key] !== null) {
      el.value = m2[m2Key];
    }
  });

  showToast('ok', `📥 Đã nạp dữ liệu từ M2: T₁=${m2.T2 ?? '—'} N·mm, n₁=${m2.n2 ?? '—'} rpm`);
}


// ─────────────────────────────────────────────────────────────
// 3. READ INPUT  –  Lấy thông số từ người dùng
// ─────────────────────────────────────────────────────────────

/**
 * Đọc toàn bộ input từ form, parse sang Number.
 * Trả về { params, errors } trong đó errors là mảng key bị thiếu/sai.
 *
 * @returns {{ params: Object, errors: string[] }}
 */
function readInput() {
  const params = {};
  const errors = [];

  Object.entries(INPUT_MAP).forEach(([htmlId, paramKey]) => {
    const el = document.getElementById(htmlId);
    const val = el ? parseFloat(el.value) : NaN;
    if (isNaN(val)) {
      errors.push(paramKey);
    } else {
      params[paramKey] = val;
    }
  });

  return { params, errors };
}

/**
 * Kiểm tra logic cơ bản của tham số trước khi tính.
 *
 * @param {Object} params
 * @returns {string[]} danh sách cảnh báo (không chặn tính)
 */
function validateParams(params) {
  const warnings = [];

  if (params.u < 1 || params.u > 6.3)
    warnings.push(`u = ${params.u} nằm ngoài khuyến nghị [1 – 6.3]`);

  if (params.K_be < 0.25 || params.K_be > 0.35)
    warnings.push(`K_be = ${params.K_be} nằm ngoài khuyến nghị [0.25 – 0.35]`);

  if (params.HB1 < params.HB2)
    warnings.push('Thông thường HB₁ ≥ HB₂ (bánh nhỏ cứng hơn bánh lớn)');

  if (params.T1 <= 0)
    warnings.push('Mô men xoắn T₁ phải > 0');

  return warnings;
}


// ─────────────────────────────────────────────────────────────
// 4. CALCULATION  –  Gọi engine tính toán
// ─────────────────────────────────────────────────────────────

/**
 * Wrapper gọi hàm calculate() từ formulas.js (hoặc inline trong HTML).
 * Nếu formulas.js không tồn tại thì fallback về hàm global.
 *
 * @param {Object} params
 * @returns {Object} kết quả R
 */
function runCalculation(params) {
  if (typeof calculate === 'function') {
    return calculate(params);
  }
  throw new Error('Không tìm thấy engine tính toán. Kiểm tra formulas.js.');
}


// ─────────────────────────────────────────────────────────────
// 5. STRENGTH CHECK  –  Đánh giá kết quả bền
// ─────────────────────────────────────────────────────────────

/**
 * Từ kết quả R, trả về object tóm tắt trạng thái kiểm nghiệm.
 *
 * @param {Object} R  kết quả từ calculate()
 * @returns {{ overall: boolean, details: Object[] }}
 */
function evaluateStrength(R) {
  const checks = [
    { name: 'Tiếp xúc σH',     pass: R.dat_H,     val: R.sigH,      limit: R.sigH_cp      },
    { name: 'Uốn σF1',         pass: R.dat_F1,    val: R.sigF1,     limit: R.sigF_cp1     },
    { name: 'Uốn σF2',         pass: R.dat_F2,    val: R.sigF2,     limit: R.sigF_cp2     },
    { name: 'Quá tải σH_max',  pass: R.dat_Hmax,  val: R.sigH_max,  limit: R.sigH_max_cp  },
    { name: 'Quá tải σF1_max', pass: R.dat_F1max, val: R.sigF1_max, limit: R.sigF_max_cp1 },
    { name: 'Quá tải σF2_max', pass: R.dat_F2max, val: R.sigF2_max, limit: R.sigF_max_cp2 },
  ];

  const overall = checks.every(c => c.pass);
  return { overall, checks };
}


// ─────────────────────────────────────────────────────────────
// 6. DISPLAY RESULT  –  Cập nhật giao diện
// ─────────────────────────────────────────────────────────────

/** Định dạng số thực */
const fmt  = (v, d = 3) => (isNaN(v) ? '—' : (+v).toFixed(d));
const fmtN = (v)        => (isNaN(v) ? '—' : Math.round(v).toString());

/** Gán textContent an toàn */
function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

/** Đặt class trạng thái bước tính */
function setStepState(stepNum, state) {
  const el = document.getElementById(`s${stepNum}num`);
  if (el) el.className = `step-num s-${state}`;
}

/** Hiển thị chip kết quả bên dưới mỗi bước */
function showStepResult(stepNum, chips) {
  const el = document.getElementById(`s${stepNum}result`);
  if (!el) return;
  el.style.display = 'flex';
  el.innerHTML = chips
    .filter(Boolean)
    .map(c => `<div class="res-chip">${c}</div>`)
    .join('');
}

/**
 * Cập nhật một hàng trong bảng kiểm nghiệm bền.
 *
 * @param {string} valId    id ô hiển thị giá trị
 * @param {string} stateId  id ô badge PASS/FAIL
 * @param {number} val      giá trị tính được
 * @param {number} limit    giới hạn cho phép
 * @param {string} unit     đơn vị hiển thị
 * @param {boolean|null} passOverride  nếu null thì tự so sánh val ≤ limit
 */
function updateCheckRow(valId, stateId, val, limit, unit = 'MPa', passOverride = null) {
  setText(valId, `${fmt(val)} ${unit}`);
  const ok  = passOverride !== null ? passOverride : val <= limit;
  const el  = document.getElementById(stateId);
  if (!el) return;
  el.className  = `check-state ${ok ? 'pass' : 'fail'}`;
  el.textContent = ok ? 'PASS ✓' : 'FAIL ✗';
}

/**
 * Cập nhật toàn bộ giao diện sau khi có kết quả R.
 *
 * @param {Object} R         kết quả từ runCalculation()
 * @param {Object} params    tham số đầu vào
 */
function displayResult(R, params) {
  // ── Bước 1: ứng suất cho phép ──────────────────────────────
  setStepState(1, 'done');
  setText('rSHL1', fmt(R.sigHlim1, 1));  setText('rSHL2', fmt(R.sigHlim2, 1));
  setText('rSFL1', fmt(R.sigFlim1, 1));  setText('rSFL2', fmt(R.sigFlim2, 1));
  setText('rNHO1', (R.N_HO1 / 1e6).toFixed(2) + 'M');
  setText('rNHO2', (R.N_HO2 / 1e6).toFixed(2) + 'M');
  setText('rKHL1', fmt(R.K_HL1, 4));  setText('rKHL2', fmt(R.K_HL2, 4));
  setText('rSHCP1', fmt(R.sigH_cp1, 2));  setText('rSHCP2', fmt(R.sigH_cp2, 2));
  setText('rSHCPdung', `${fmt(R.sigH_cp, 2)} MPa`);
  setText('rSFCP1', fmt(R.sigF_cp1, 2));  setText('rSFCP2', fmt(R.sigF_cp2, 2));
  showStepResult(1, [
    `[σH] = ${fmt(R.sigH_cp, 2)} MPa`,
    `[σF]₁ = ${fmt(R.sigF_cp1, 2)} MPa`,
    `[σF]₂ = ${fmt(R.sigF_cp2, 2)} MPa`,
  ]);

  // ── Bước 2: chiều dài côn sơ bộ ────────────────────────────
  setStepState(2, 'done');
  showStepResult(2, [
    `Re_sb = ${fmt(R.Re_sb, 3)} mm`,
    `K_Hβ = ${fmt(R.K_Hbeta, 4)}`,
    `K_Fβ = ${fmt(R.K_Fbeta, 4)}`,
    `b = ${fmt(R.b_fixed, 3)} mm`,
  ]);

  // ── Bước 3: thông số ăn khớp ────────────────────────────────
  setStepState(3, 'done');
  showStepResult(3, [
    `Z₁ = ${R.Z1}  Z₂ = ${R.Z2}`,
    `mte = ${R.mte} mm`,
    `Re = ${fmt(R.Re, 3)} mm`,
    `dm1 = ${fmt(R.dm1, 4)} mm`,
    `b = ${fmt(R.b, 3)} mm`,
  ]);

  // ── Bước 4: kiểm nghiệm tiếp xúc ───────────────────────────
  setStepState(4, R.dat_H ? 'done' : 'active');
  showStepResult(4, [
    `v = ${fmt(R.v, 3)} m/s · CCX ${R.cap_cx}`,
    `K_H = ${fmt(R.K_H, 4)}`,
    `K_Hv = ${fmt(R.K_Hv, 4)}`,
    `σH = ${fmt(R.sigH, 3)} MPa`,
    R.dat_H
      ? `✓ Đạt (chênh ${fmt(R.chenh, 1)}%)`
      : `⚠ Vượt ${fmt(R.chenh, 1)}%`,
    R.iterCount > 0 ? `Đã tăng mte ${R.iterCount} lần` : '',
  ]);

  // ── Bước 5: kiểm nghiệm uốn ─────────────────────────────────
  setStepState(5, (R.dat_F1 && R.dat_F2) ? 'done' : 'active');
  showStepResult(5, [
    `K_F = ${fmt(R.K_F, 4)}`,
    `K_Fv = ${fmt(R.K_Fv, 4)}`,
    `YF1 = ${fmt(R.YF1, 3)}  YF2 = ${fmt(R.YF2, 3)}`,
    `σF1 = ${fmt(R.sigF1, 3)} MPa`,
    `σF2 = ${fmt(R.sigF2, 3)} MPa`,
  ]);

  // ── Bước 6: kiểm nghiệm quá tải ─────────────────────────────
  setStepState(6, (R.dat_Hmax && R.dat_F1max && R.dat_F2max) ? 'done' : 'active');
  showStepResult(6, [
    `σH_max = ${fmt(R.sigH_max, 3)} / ${fmt(R.sigH_max_cp, 1)} MPa`,
    `σF1_max = ${fmt(R.sigF1_max, 3)} / ${fmt(R.sigF_max_cp1, 1)} MPa`,
    `σF2_max = ${fmt(R.sigF2_max, 3)} / ${fmt(R.sigF_max_cp2, 1)} MPa`,
  ]);

  // ── Bảng kiểm nghiệm bền ────────────────────────────────────
  // Vận tốc
  setText('ckV', `${fmt(R.v, 3)} m/s`);
  const ckVs = document.getElementById('ckVs');
  if (ckVs) { ckVs.className = 'check-state pass'; ckVs.textContent = `CCX ${R.cap_cx}`; }

  setText('ckSHlim',    `${fmt(R.sigH_cp, 2)} MPa`);
  setText('ckSF1lim',   `${fmt(R.sigF_cp1, 2)} MPa`);
  setText('ckSF2lim',   `${fmt(R.sigF_cp2, 2)} MPa`);
  setText('ckSHmaxLim', `${fmt(R.sigH_max_cp, 1)} MPa`);
  setText('ckSF1maxLim',`${fmt(R.sigF_max_cp1, 1)} MPa`);
  setText('ckSF2maxLim',`${fmt(R.sigF_max_cp2, 1)} MPa`);

  updateCheckRow('ckSH',     'ckSHs',     R.sigH,      R.sigH_cp,      'MPa', R.dat_H);
  updateCheckRow('ckSF1',    'ckSF1s',    R.sigF1,     R.sigF_cp1,     'MPa', R.dat_F1);
  updateCheckRow('ckSF2',    'ckSF2s',    R.sigF2,     R.sigF_cp2,     'MPa', R.dat_F2);
  updateCheckRow('ckSHmax',  'ckSHmaxs',  R.sigH_max,  R.sigH_max_cp,  'MPa', R.dat_Hmax);
  updateCheckRow('ckSF1max', 'ckSF1maxs', R.sigF1_max, R.sigF_max_cp1, 'MPa', R.dat_F1max);
  updateCheckRow('ckSF2max', 'ckSF2maxs', R.sigF2_max, R.sigF_max_cp2, 'MPa', R.dat_F2max);

  // ── Hệ số động học ──────────────────────────────────────────
  setText('hKHb', fmt(R.K_Hbeta, 4));  setText('hKFb', fmt(R.K_Fbeta, 4));
  setText('hKHv', fmt(R.K_Hv,    4));  setText('hKFv', fmt(R.K_Fv,    4));
  setText('hKH',  fmt(R.K_H,     4));  setText('hKF',  fmt(R.K_F,     4));
  setText('hZH',  fmt(R.ZH,      4));  setText('hEps', fmt(R.eps_alpha,4));
  setText('hZe',  fmt(R.Z_eps,   4));  setText('hYe',  fmt(R.Y_eps,   4));
  setText('hYF1', fmt(R.YF1,     4));  setText('hYF2', fmt(R.YF2,     4));

  // ── Kết quả tổng hợp (result panel) ─────────────────────────
  setText('rRe',  fmt(R.Re, 3));
  setText('rRe_sb', `Re_sb = ${fmt(R.Re_sb, 3)} mm`);
  setText('rMte', fmt(R.mte, 4));
  setText('rMtm_sub', `mtm = ${fmt(R.mtm, 4)} mm`);
  setText('rZ',   `${R.Z1} / ${R.Z2}`);
  setText('rU',   `u_tt = ${fmt(R.u_tt, 4)}  (Δ${fmt(R.sai_so_u, 2)}%)`);
  setText('rB',   fmt(R.b, 3));
  setText('rBcheck', `b/Re = ${fmt(R.b_Re, 3)} ${R.b_Re >= 0.25 && R.b_Re <= 0.35 ? '✓' : '⚠'}`);

  // ── Bảng output chi tiết ────────────────────────────────────
  buildOutputTable(R, params);

  // ── Hiện panel kết quả ──────────────────────────────────────
  const panel = document.getElementById('resultPanel');
  if (panel) panel.style.display = 'block';

  const aiContainer = document.getElementById('aiDoctorConContainer');
const aiDetails = document.getElementById('aiDiagnosticDetails');
const aiRawMte = document.getElementById('aiRawMte');
const aiSuggestedMte = document.getElementById('aiSuggestedMte');

// Kiểm tra xem có điều kiện nào không đạt hay không (dựa vào R.dat_all)
if (!R.dat_all) {
  // 1. Hiện khối AI
  if (aiContainer) aiContainer.style.display = 'block';
  
  // 2. Điền chi tiết lỗi
  const fails = buildFailList(R); // Sử dụng hàm buildFailList đã có sẵn
  if (aiDetails) {
    aiDetails.innerHTML = fails.map(fail => `<li>Tham số <b>${fail}</b> không đạt yêu cầu.</li>`).join('');
  }
  
  // 3. Gợi ý thông số (Ví dụ: đề xuất tăng module)
  if (aiRawMte) aiRawMte.textContent = (R.mte).toFixed(2);
  if (aiSuggestedMte) aiSuggestedMte.textContent = (R.mte + 0.5).toFixed(2); // Logic tính module đề xuất của bạn

} else {
  // Nếu tất cả đều đạt, ẩn khối AI đi
  if (aiContainer) aiContainer.style.display = 'none';
}
}

/**
 * Xây dựng bảng thông số đầy đủ trong result panel.
 *
 * @param {Object} R
 * @param {Object} params
 */
function buildOutputTable(R, params) {
  const tbody = document.getElementById('outputTableBody');
  if (!tbody) return;

  const sections = [
    { sect: 'THÔNG SỐ HÌNH HỌC' },
    { label: 'Chiều dài côn ngoài Re',          val: fmt(R.Re, 3),       unit: 'mm' },
    { label: 'Chiều dài côn ngoài sơ bộ Re_sb', val: fmt(R.Re_sb, 3),   unit: 'mm' },
    { label: 'Module mặt đầu ngoài mte',         val: fmt(R.mte, 4),     unit: 'mm' },
    { label: 'Module trung bình mtm',             val: fmt(R.mtm, 4),     unit: 'mm' },
    { label: 'Chiều rộng vành răng b',            val: fmt(R.b, 3),       unit: 'mm' },
    { label: 'Tỉ số truyền yêu cầu u',           val: fmt(params.u, 4),  unit: '—'  },
    { label: 'Tỉ số truyền thực u_tt',           val: fmt(R.u_tt, 4),    unit: '—'  },
    { label: 'Sai số tỉ số truyền Δu',           val: fmt(R.sai_so_u, 2),unit: '%'  },
    { label: 'Số răng bánh nhỏ Z₁',              val: fmtN(R.Z1),        unit: 'răng'},
    { label: 'Số răng bánh lớn Z₂',              val: fmtN(R.Z2),        unit: 'răng'},

    { sect: 'ĐƯỜNG KÍNH' },
    { label: 'Đường kính ngoài bánh nhỏ de1',    val: fmt(R.de1, 3),  unit: 'mm' },
    { label: 'Đường kính ngoài bánh lớn de2',    val: fmt(R.de2, 3),  unit: 'mm' },
    { label: 'Đường kính trung bình bánh nhỏ dm1',val: fmt(R.dm1, 4), unit: 'mm' },
    { label: 'Đường kính trung bình bánh lớn dm2',val: fmt(R.dm2, 4), unit: 'mm' },
    { label: 'Đường kính đỉnh răng dae1',        val: fmt(R.dae1, 3), unit: 'mm' },
    { label: 'Đường kính đỉnh răng dae2',        val: fmt(R.dae2, 3), unit: 'mm' },

    { sect: 'GÓC VÀ CHIỀU CAO RĂNG' },
    { label: 'Góc côn chia bánh nhỏ δ₁',         val: fmt(R.delta1_deg, 3), unit: '°' },
    { label: 'Góc côn chia bánh lớn δ₂',          val: fmt(R.delta2_deg, 3), unit: '°' },
    { label: 'Chiều cao răng ngoài he',            val: fmt(R.he, 4),  unit: 'mm' },
    { label: 'Chiều cao đầu răng ngoài hae',       val: fmt(R.hae, 4), unit: 'mm' },
    { label: 'Chiều cao chân răng ngoài hfe',      val: fmt(R.hfe, 4), unit: 'mm' },

    { sect: 'KIỂM NGHIỆM BỀN' },
    { label: 'Vận tốc vòng v',                    val: fmt(R.v, 3),         unit: 'm/s' },
    { label: 'Cấp chính xác',                     val: fmtN(R.cap_cx),      unit: '—'   },
    { label: 'Ứng suất tiếp xúc σH / [σH]',      val: `${fmt(R.sigH,3)} / ${fmt(R.sigH_cp,3)}`,     unit: 'MPa' },
    { label: 'Ứng suất uốn σF1 / [σF]₁',         val: `${fmt(R.sigF1,3)} / ${fmt(R.sigF_cp1,3)}`,   unit: 'MPa' },
    { label: 'Ứng suất uốn σF2 / [σF]₂',         val: `${fmt(R.sigF2,3)} / ${fmt(R.sigF_cp2,3)}`,   unit: 'MPa' },
    { label: 'Quá tải σH_max / [σH]max',          val: `${fmt(R.sigH_max,3)} / ${fmt(R.sigH_max_cp,3)}`,   unit: 'MPa' },
    { label: 'Quá tải σF1_max / [σF1]max',        val: `${fmt(R.sigF1_max,3)} / ${fmt(R.sigF_max_cp1,3)}`, unit: 'MPa' },
    { label: 'Quá tải σF2_max / [σF2]max',        val: `${fmt(R.sigF2_max,3)} / ${fmt(R.sigF_max_cp2,3)}`, unit: 'MPa' },

    { sect: 'HỆ SỐ TẢI TRỌNG' },
    { label: 'K_Hβ',             val: fmt(R.K_Hbeta, 4), unit: '—' },
    { label: 'K_Fβ',             val: fmt(R.K_Fbeta, 4), unit: '—' },
    { label: 'K_Hv',             val: fmt(R.K_Hv, 4),    unit: '—' },
    { label: 'K_Fv',             val: fmt(R.K_Fv, 4),    unit: '—' },
    { label: 'K_H = K_Hβ·K_Hα·K_Hv', val: fmt(R.K_H, 4), unit: '—' },
    { label: 'K_F = K_Fβ·K_Fα·K_Fv', val: fmt(R.K_F, 4), unit: '—' },
    { label: 'Z_H',              val: fmt(R.ZH, 4),       unit: '—' },
    { label: 'Z_ε',              val: fmt(R.Z_eps, 4),    unit: '—' },
    { label: 'ε_α',              val: fmt(R.eps_alpha, 4),unit: '—' },
    { label: 'Y_ε = 1/ε_α',     val: fmt(R.Y_eps, 4),    unit: '—' },
    { label: 'Y_F1 (Z₁ tương đương)', val: fmt(R.YF1, 3),unit: '—' },
    { label: 'Y_F2 (Z₂ tương đương)', val: fmt(R.YF2, 3),unit: '—' },
  ];

  tbody.innerHTML = sections.map(row => {
    if (row.sect) {
      return `<tr class="section-row"><td colspan="3">${row.sect}</td></tr>`;
    }
    return `
      <tr>
        <td>${row.label}</td>
        <td class="num-val" style="text-align:right;">${row.val}</td>
        <td class="unit-col">${row.unit}</td>
      </tr>`;
  }).join('');
}


// ─────────────────────────────────────────────────────────────
// 7. SAVE DATA  –  Lưu M3_Data
// ─────────────────────────────────────────────────────────────

/**
 * Đóng gói kết quả thành M3_Data chuẩn và lưu vào storage.
 * Dữ liệu này sẽ được M4 đọc.
 *
 * @param {Object} R       kết quả từ calculate()
 * @param {Object} params  tham số đầu vào
 */
function saveM3Data(R, params) {
  const M3_Data = {
    // ── Truyền sang M4 ─────────────────────────────────────
    P3:  params.T1 * params.n1 / 9550000,   // kW (gần đúng, M4 nên tính lại)
    n3:  params.n1 / R.u_tt,                 // rpm trục ra

    T1: params.T1,
    n1: params.n1,

    // ── Hình học ────────────────────────────────────────────
    z1:  R.Z1,
    z2:  R.Z2,
    u_con: R.u_tt,

    mte: R.mte,
    mtm: R.mtm,

    Re:  R.Re,
    b:   R.b,

    de1: R.de1,
    de2: R.de2,
    dm1: R.dm1,
    dm2: R.dm2,

    delta1_deg: R.delta1_deg,
    delta2_deg: R.delta2_deg,

    dae1: R.dae1,
    dae2: R.dae2,
    he:   R.he,
    hae:  R.hae,
    hfe:  R.hfe,

    // ── Bền ─────────────────────────────────────────────────
    sigH:     R.sigH,
    sigF1:    R.sigF1,
    sigF2:    R.sigF2,
    sigH_max: R.sigH_max,

    // ── Trạng thái ──────────────────────────────────────────
    dat_all: R.dat_all,
    status:  R.dat_all ? 'Đạt' : 'Không đạt',

    // ── Meta ─────────────────────────────────────────────────
    calculatedAt: new Date().toISOString(),
  };

  try {
    if (typeof saveData === 'function') {
      saveData(M3_KEY, M3_Data);
    } else {
      localStorage.setItem(M3_KEY, JSON.stringify(M3_Data));
    }
    console.info('[M3] Đã lưu M3_Data:', M3_Data);
  } catch (err) {
    console.error('[M3] Lỗi lưu M3_Data:', err);
    showToast('error', '⚠️ Không thể lưu M3_Data vào storage!');
  }

  return M3_Data;
}


// ─────────────────────────────────────────────────────────────
// 8. NEXT MODULE  –  Chuyển sang M4
// ─────────────────────────────────────────────────────────────

/**
 * Điều hướng sang Module 4 (bánh răng trụ).
 * Ưu tiên gọi workflow.js nếu tồn tại, fallback về location.href.
 */
function goToM4() {
  if (typeof window.navigateTo === 'function') {
    window.navigateTo('../m4/UI_banhrangtru.html');
    return;
  }
  if (typeof goToModule === 'function') {
    goToModule('M4');
    return;
  }
  window.location.href = '../m4/UI_banhrangtru.html';
}


// ─────────────────────────────────────────────────────────────
// STATUS BAR  –  Cập nhật thanh trạng thái
// ─────────────────────────────────────────────────────────────

/**
 * @param {'idle'|'running'|'ok'|'err'} state
 * @param {string} title
 * @param {string} sub
 */
function setStatus(state, title, sub = '') {
  const dot = document.getElementById('statusDot');
  const txt = document.getElementById('statusText');
  const subEl = document.getElementById('statusSub');
  if (dot)   dot.className  = `status-dot ${state}`;
  if (txt)   txt.textContent = title;
  if (subEl) subEl.textContent = sub;
}


// ─────────────────────────────────────────────────────────────
// PUBLIC API  –  Các hàm gọi từ HTML onclick
// ─────────────────────────────────────────────────────────────

/**
 * runCalc()  —  Gọi từ nút "Tính toán"
 * Orchestrate toàn bộ pipeline M3.
 */
function runCalc() {
  // 3. Đọc input
  const { params, errors } = readInput();

  if (errors.length > 0) {
    showToast('error', `❌ Thiếu hoặc sai định dạng: ${errors.join(', ')}`);
    return;
  }

  // Validate logic
  const warnings = validateParams(params);
  warnings.forEach(w => showToast('warn', `⚠️ ${w}`));

  // UI: bắt đầu tính
  setStatus('running', '⏳ Đang tính toán...', 'Vòng lặp kiểm nghiệm σH đang chạy');
  for (let i = 1; i <= STEP_COUNT; i++) setStepState(i, 'active');

  // Dùng setTimeout để browser kịp render animation trước khi tính
  setTimeout(() => {
    try {
      // 4. Tính toán
      const R = runCalculation(params);

      // 5. Đánh giá bền
      const { overall } = evaluateStrength(R);

      // 6. Hiển thị kết quả
      displayResult(R, params);

      // Cập nhật status bar
      if (overall) {
        setStatus(
          'ok',
          '✅ Tính toán hoàn tất – TẤT CẢ ĐẠT YÊU CẦU',
          `mte=${R.mte}mm · Z₁=${R.Z1} · Z₂=${R.Z2} · Re=${fmt(R.Re,2)}mm · dm1=${fmt(R.dm1,2)}mm`,
        );
      } else {
        const fails = buildFailList(R);
        setStatus(
          'err',
          '⚠️ Một số điều kiện CHƯA ĐẠT',
          `Không đạt: ${fails.join(', ')}`,
        );
      }

      // Toast thông tin đặc biệt
      if (R.iterCount > 0)
        showToast('warn', `⚠️ Đã tăng module ${R.iterCount} lần → mte = ${R.mte} mm`);

      if (overall) {
        // 7. Lưu dữ liệu
        saveM3Data(R, params);

        // Kích hoạt nút Next
        const btnNext = document.getElementById('btnNext');
        if (btnNext) {
          btnNext.removeAttribute('disabled');
        }

        

        showToast('ok', '✅ M3 hoàn tất! Dữ liệu đã lưu. Sẵn sàng chuyển M4.');
      } else {
        const fails = buildFailList(R);
        showToast('error', `❌ Chưa đạt: ${fails.join(', ')} — Trợ lý AI đang phân tích...`);

        // --- BẮT ĐẦU LOGIC AI DOCTOR (M3) ---
        // 1. KHAI BÁO TRƯỚC RỒI MỚI GỌI (Fix lỗi crash JS)
        const aiContainer = document.getElementById('aiDoctorConContainer');
        if (aiContainer) {
            aiContainer.style.setProperty('display', 'block', 'important');
        }

        let inputErrors = [];

        // 2. Chẩn đoán theo KẾT QUẢ KIỂM NGHIỆM (Chỉ mặt điểm tên)
        if (!R.dat_H) {
            inputErrors.push(`📍 <b>Rỗ bề mặt (σH vượt mức):</b> Ứng suất tiếp xúc lớn hơn cho phép. 
            <br>👉 <i>Khắc phục:</i> Tăng <b>Mô-đun (mte)</b>, tăng <b>Hệ số Kbe</b>, hoặc chọn vật liệu có <b>Độ cứng HB/HRC cao hơn</b>.`);
        }
        
        if (!R.dat_F1 || !R.dat_F2) {
            inputErrors.push(`📍 <b>Nguy cơ gãy chân răng (σF vượt mức):</b> Ứng suất uốn quá lớn. 
            <br>👉 <i>Khắc phục:</i> Tăng <b>Mô-đun (mte)</b>, hoặc tăng <b>Số răng (z₁, z₂)</b>.`);
        }

        if (!R.dat_Hmax || !R.dat_F1max || !R.dat_F2max) {
            // Nhận diện lỗi cấu trúc hình học nếu ứng suất max phi lý
            let isAbsurdlyHigh = false;
            if (R.sigF1_max && params.sigCh1 && R.sigF1_max > params.sigCh1 * 5) isAbsurdlyHigh = true;

            if (isAbsurdlyHigh) {
                inputErrors.push(`📍 <b>Quá tải mức độ NGHIÊM TRỌNG:</b> Ứng suất sinh ra lớn gấp hàng chục lần sức chịu đựng.
                <br>👉 <i>Nguyên nhân:</i> Mâu thuẫn cấu trúc hình học. Hãy kiểm tra lại <b>Mô-đun (mte)</b>, <b>Số răng (z)</b> và hệ số truyền!`);
            } else {
                inputErrors.push(`📍 <b>Quá tải phá hủy:</b> Lực va đập vượt sức chịu đựng. 
                <br>👉 <i>Khắc phục:</i> Giảm <b>Hệ số Kqt</b>, hoặc tăng <b>Giới hạn chảy (σ_ch)</b>.`);
            }
        }

        // Bắt thêm lỗi tương quan độ cứng nếu nhập ngược
        if (params.HB1 <= params.HB2) {
            inputErrors.push(`📍 <b>Tương quan độ cứng bị ngược:</b> Bánh dẫn (HB1) đang mềm hơn hoặc bằng Bánh bị dẫn. Hãy chỉnh <b>HB1 > HB2</b>.`);
        }

        // Cập nhật danh sách lỗi lên giao diện
        const detailsContainer = document.getElementById('aiDiagnosticDetails');
        if (detailsContainer) {
            detailsContainer.innerHTML = '';
            if (inputErrors.length === 0) inputErrors.push("📍 <b>Lỗi thông số:</b> Vui lòng kiểm tra lại sự đồng bộ tải trọng.");
            inputErrors.forEach(errStr => {
                let li = document.createElement('li');
                li.innerHTML = errStr;
                li.style.marginBottom = "12px";
                li.style.lineHeight = "1.5";
                detailsContainer.appendChild(li);
            });
        }

        // Set trạng thái Loading cho API
        if(document.getElementById('aiRawMte')) document.getElementById('aiRawMte').textContent = "Đang tính toán...";
        if(document.getElementById('aiSuggestedMte')) document.getElementById('aiSuggestedMte').textContent = "Đang phân tích...";

        // 3. Tiến hành gọi API
        let safeSigH = (isNaN(R.sigH) || !isFinite(R.sigH)) ? 1000 : R.sigH;
        let safeSallow = (isNaN(R.sigH_cp) || R.sigH_cp <= 0) ? 400 : R.sigH_cp;
        let thuc_te_overload = safeSigH / safeSallow;
        if (isNaN(thuc_te_overload) || thuc_te_overload < 1.0) thuc_te_overload = 1.15;

        const aiPayload = {
            T1: params.T1,
            u: params.u,
            mte_loi: R.mte || params.mte || 3,
            z1: R.Z1,
            HB1: params.HB1 > 600 ? 250 : params.HB1, 
            overload_ratio: parseFloat(thuc_te_overload.toFixed(2))
        };

        fetch('http://127.0.0.1:8000/api/v1/predict/bevel-gear', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(aiPayload)
        })
        .then(res => { if (!res.ok) throw new Error("Backend lỗi"); return res.json(); })
        .then(response => {
            if (response.status === 'success') {
                document.getElementById('aiRawMte').textContent = response.data.raw_predicted_mte || "N/A";
                document.getElementById('aiSuggestedMte').textContent = response.data.suggested_mte || "N/A";
            }
        })
        .catch(err => {
            console.warn("Chạy AI Offline:", err);
            let mte_base = R.mte || params.mte || 3;
            let standardMte = Math.ceil((mte_base + 0.5) * 2) / 2;
            if(document.getElementById('aiRawMte')) document.getElementById('aiRawMte').textContent = (mte_base * Math.sqrt(thuc_te_overload)).toFixed(2) + " (Sơ bộ)";
            if(document.getElementById('aiSuggestedMte')) document.getElementById('aiSuggestedMte').textContent = `${standardMte} mm (Gợi ý)`;
        });
      }


    } catch (err) {
      setStatus('err', `❌ Lỗi tính toán: ${err.message}`);
      showToast('error', `❌ Lỗi: ${err.message}`);
      console.error('[M3] Lỗi tính toán:', err);
    }
  }, 80);
}

/**
 * resetAll()  —  Gọi từ nút "Đặt lại"
 */
function resetAll() {
  const aiContainer = document.getElementById('aiDoctorConContainer');
  if (aiContainer) aiContainer.style.setProperty('display', 'none', 'important');

  for(let i=1;i<=6;i++) { setStepState('s'+i+'num','s-idle'); document.getElementById('s'+i+'result').style.display='none'; }
  document.getElementById('resultPanel').style.display='none';
  // Reset bước tính
  for (let i = 1; i <= STEP_COUNT; i++) {
    setStepState(i, 'idle');
    const resEl = document.getElementById(`s${i}result`);
    if (resEl) resEl.style.display = 'none';
  }

  // Reset bảng kết quả
  const panel = document.getElementById('resultPanel');
  if (panel) panel.style.display = 'none';

  const tbody = document.getElementById('outputTableBody');
  if (tbody) {
    tbody.innerHTML = '<tr><td colspan="3" style="text-align:center;color:var(--tx3);padding:30px;">Chưa có kết quả</td></tr>';
  }

  // Reset status bar
  setStatus('idle', 'Nhập thông số và nhấn "Tính toán"', 'Cần điền đầy đủ: T₁, n₁, u, t_h và vật liệu');

  // Reset bảng ứng suất
  RESULT_IDS.forEach(id => setText(id, '—'));

  // Reset badge kiểm nghiệm
  CHECK_IDS.forEach(id => {
    const el = document.getElementById(id);
    if (el) { el.className = 'check-state idle'; el.textContent = 'IDLE'; }
  });

  // Reset nút Next
  const btnNext = document.getElementById('btnNext');
  if (btnNext) btnNext.setAttribute('disabled', 'true');

  // Reset limit cells
  ['ckSHlim','ckSF1lim','ckSF2lim','ckSHmaxLim','ckSF1maxLim','ckSF2maxLim'].forEach(id => setText(id, '— MPa'));
}


// ─────────────────────────────────────────────────────────────
// HELPER NỘI BỘ
// ─────────────────────────────────────────────────────────────

/** Trả về danh sách điều kiện không đạt */
function buildFailList(R) {
  const fails = [];
  if (!R.dat_H)    fails.push('σH tiếp xúc');
  if (!R.dat_F1)   fails.push('σF1 uốn');
  if (!R.dat_F2)   fails.push('σF2 uốn');
  if (!R.dat_Hmax) fails.push('σH_max quá tải');
  if (!R.dat_F1max)fails.push('σF1_max quá tải');
  if (!R.dat_F2max)fails.push('σF2_max quá tải');
  return fails;
}

/**
 * showToast()  —  Hiển thị thông báo toast
 * Dùng engine toast đã có trong HTML, hoặc console fallback.
 *
 * @param {'ok'|'error'|'warn'} type
 * @param {string} msg
 */
function showToast(type, msg) {
  const wrap = document.getElementById('toastWrap');
  if (!wrap) { console[type === 'error' ? 'error' : 'info']('[M3 Toast]', msg); return; }

  const icons = { ok: '✅', error: '❌', warn: '⚠️' };
  const t = document.createElement('div');
  t.className = `toast toast-${type}`;
  t.innerHTML = `
    <span class="toast-icon">${icons[type] ?? 'ℹ️'}</span>
    <span class="toast-msg">${msg}</span>
    <span class="toast-close" onclick="this.parentElement.remove()">✕</span>`;
  wrap.appendChild(t);

  setTimeout(() => {
    t.style.opacity    = '0';
    t.style.transform  = 'translateX(16px)';
    t.style.transition = 'all 0.28s';
    setTimeout(() => t.remove(), 300);
  }, 6000);
}


// ─────────────────────────────────────────────────────────────
// ENTRY POINT  –  Tự động chạy khi DOM sẵn sàng
// ─────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  console.info('[M3] BanhRangCon module khởi động.');

  // 1. Đọc M2
  const m2 = loadM2Data();

  // 2. Init UI
  initUI(m2);

  // Gán sự kiện cho nút Next (phòng trường hợp onclick không có trong HTML)
  const btnNext = document.getElementById('btnNext');
  if (btnNext) {
    btnNext.addEventListener('click', (e) => {
      e.preventDefault();
      goToM4();
    });
  }

  console.info('[M3] Khởi tạo hoàn tất. Chờ người dùng nhập thông số.');
});
