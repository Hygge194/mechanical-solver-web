/**
 * ============================================================
 *  M4_BanhRangTru.js  —  Controller của Module 4
 *  Bộ truyền bánh răng trụ – Răng thẳng
 * ============================================================
 *
 *  Kiến trúc phụ thuộc:
 *    storage.js   → loadData(key) / saveData(key, obj)
 *    formulas.js  → các hàm tính (gearGeometry, V1..V5, ...)
 *    workflow.js  → goToModule(id) / exportReport()
 *
 *  File này KHÔNG chứa:
 *    - Công thức cơ khí
 *    - CSS / HTML string thuần
 *
 *  File này CHỈ làm:
 *    - Điều phối luồng dữ liệu giữa UI, formulas.js và storage.js
 *    - Tổng hợp báo cáo hệ thống từ M1 → M4
 * ============================================================
 */

// ─────────────────────────────────────────────────────────────
// CONSTANTS
// ─────────────────────────────────────────────────────────────

const M3_KEY = 'M3_Data';
const M4_KEY = 'M4_Data';

/** Mapping id HTML → key trong params object */
const INPUT_MAP = {
  T1:      'T1',
  T1sb:    'T1sb',
  u_yc:    'u_yc',
  Kqt:     'Kqt',
  n1v:     'n1v',
  d1v:     'd1v',
  sHlim1:  'sHlim1',  sFlim1:  'sFlim1',  sch1: 'sch1',
  SH1:     'SH1',     KHL1:    'KHL1',
  SF1:     'SF1',     KFL1:    'KFL1',
  sHlim2:  'sHlim2',  sFlim2:  'sFlim2',  sch2: 'sch2',
  SH2:     'SH2',     KHL2:    'KHL2',
  SF2:     'SF2',     KFL2:    'KFL2',
  aw:      'aw',
  psi_a:   'psi_a',
  z1:      'z1',      z2:      'z2',
  x1:      'x1',      x2:      'x2',
  KHb:     'KHb',     KHa:     'KHa',     KHv: 'KHv',
  KFb:     'KFb',     KFa:     'KFa',     KFv: 'KFv',
  KHbsb:   'KHbsb',
};

/** Ánh xạ M3_Data → ô input tương ứng */
const M3_TO_INPUT = {
  T1:    'T1',    // Mômen xoắn trục vào M4 = T ra của M3
  n3:    'n1v',   // Tốc độ trục vào M4
  dm1:   'd1v',   // d1 dùng tính vận tốc ≈ dm1 của M3
  u_con: 'u_yc',  // Tỉ số truyền yêu cầu lấy từ côn
};

/** id check-state badge cần reset */
const CHECK_STATE_IDS = [
  'ck_z1s','ck_z2s','ck_epss','ck_bwms',
  'ck_sHs','ck_sF1s','ck_sF2s','ck_sHms',
];
const CHECK_VAL_IDS = [
  'ck_z1v','ck_z2v','ck_epsv','ck_bwmv',
  'ck_sHv','ck_sF1v','ck_sF2v','ck_sHmv',
];
const CHECK_LIM_IDS = [
  'ck_sHlim','ck_sF1lim','ck_sF2lim','ck_sHmax_lim',
];

// ─────────────────────────────────────────────────────────────
// 1. LOAD PREVIOUS DATA  –  Đọc dữ liệu từ M3
// ─────────────────────────────────────────────────────────────

/**
 * Đọc M3_Data từ storage.
 * Nếu không có → cảnh báo và có thể redirect về M3.
 *
 * @param {boolean} strict  true = redirect nếu không có data
 * @returns {Object|null}
 */
function loadM3Data(strict = false) {
  let data = null;
  try {
    data = (typeof loadData === 'function')
      ? loadData(M3_KEY)
      : JSON.parse(localStorage.getItem(M3_KEY) || 'null');
  } catch (err) {
    console.error('[M4] Lỗi đọc M3_Data:', err);
  }

  if (!data) {
    console.warn('[M4] Không tìm thấy M3_Data.');
    if (strict) {
      const go = confirm('⚠️ Chưa có dữ liệu từ Module 3 (Bánh răng côn).\nChuyển về M3 để tính toán trước?');
      if (go) {
        if (typeof goToModule === 'function') goToModule('M3');
        else window.location.href = 'M3_BanhRangCon.html';
      }
    }
  }
  return data;
}

// ─────────────────────────────────────────────────────────────
// 2. INITIALIZE UI  –  Điền dữ liệu M3 vào form
// ─────────────────────────────────────────────────────────────

/**
 * Cập nhật đồng hồ topbar và điền M3_Data vào các ô input.
 *
 * @param {Object|null} m3
 */
function initUI(m3) {
  // Topbar date
  const tbDate = document.getElementById('tbDate');
  if (tbDate) {
    tbDate.textContent = new Date().toLocaleDateString('vi-VN', {
      weekday: 'short', day: '2-digit', month: '2-digit', year: 'numeric',
    });
  }

  if (!m3) return;

  // Điền từng trường từ M3
  Object.entries(M3_TO_INPUT).forEach(([m3Key, htmlId]) => {
    const el = document.getElementById(htmlId);
    if (el && m3[m3Key] !== undefined && m3[m3Key] !== null) {
      el.value = typeof m3[m3Key] === 'number'
        ? parseFloat(m3[m3Key].toFixed(4))
        : m3[m3Key];
    }
  });

  // Điền thêm T1sb nếu M3 có T1_sb riêng
  if (m3.T1_sb) {
    const elSb = document.getElementById('T1sb');
    if (elSb) elSb.value = parseFloat(m3.T1_sb.toFixed(4));
  }

  // Cập nhật gear visual ngay sau khi điền
  if (typeof updateGearVisual === 'function') updateGearVisual();

  showToast(
    'ok',
    `📥 Đã nạp từ M3: T₁=${m3.T1 ? m3.T1.toFixed(0) : '—'} N·mm, n₁=${m3.n3 ? m3.n3.toFixed(1) : '—'} rpm`,
  );
}

// ─────────────────────────────────────────────────────────────
// 3. READ INPUT  –  Đọc thông số từ form
// ─────────────────────────────────────────────────────────────

/**
 * Đọc tất cả ô input, parse Number.
 * Trả về { params, errors }.
 *
 * @returns {{ params: Object, errors: string[] }}
 */
function readInput() {
  const params  = {};
  const errors  = [];

  Object.entries(INPUT_MAP).forEach(([htmlId, paramKey]) => {
    const el = document.getElementById(htmlId);
    if (!el) return;

    // select → chuỗi, input → float
    const isSelect = el.tagName === 'SELECT';
    const val = isSelect ? el.value : parseFloat(el.value);

    if (!isSelect && isNaN(val)) {
      errors.push(paramKey);
    } else {
      params[paramKey] = val;
    }
  });

  // Đọc riêng select môđun và vật liệu (không có trong INPUT_MAP vì là string)
  const mEl    = document.getElementById('m');
  const capVLEl= document.getElementById('capVL');
  if (mEl)     params.m     = parseFloat(mEl.value) || 3.0;
  if (capVLEl) params.capVL = capVLEl.value;

  // z1, z2 phải là integer
  params.z1 = parseInt(document.getElementById('z1')?.value) || 0;
  params.z2 = parseInt(document.getElementById('z2')?.value) || 0;

  return { params, errors };
}

/**
 * Kiểm tra logic sơ bộ trước khi tính.
 * Trả về mảng cảnh báo (không chặn tính).
 *
 * @param {Object} params
 * @returns {string[]}
 */
function validateParams(params) {
  const warns = [];
  const Z_MIN = 17;

  if (params.z1 < Z_MIN)
    warns.push(`z₁ = ${params.z1} < ${Z_MIN} — có nguy cơ cắt chân răng`);
  if (params.z2 < Z_MIN)
    warns.push(`z₂ = ${params.z2} < ${Z_MIN} — có nguy cơ cắt chân răng`);
  if (params.T1 <= 0)
    warns.push('Mômen xoắn T₁ phải > 0');
  if (params.aw <= 0)
    warns.push('Khoảng cách trục a_w phải > 0');
  if (params.psi_a < 0.1 || params.psi_a > 0.6)
    warns.push(`ψa = ${params.psi_a} nằm ngoài [0.1 – 0.6]`);
  if (params.u_yc < 1 || params.u_yc > 8)
    warns.push(`u_yc = ${params.u_yc} — kiểm tra tỉ số truyền bánh răng trụ`);

  return warns;
}

// ─────────────────────────────────────────────────────────────
// 4. CALCULATE GEOMETRY  –  Gọi tính hình học
// ─────────────────────────────────────────────────────────────

/**
 * Wrapper gọi gearGeometry() từ formulas.js / inline HTML.
 *
 * @param {Object} p  params đã đọc
 * @returns {Object}  geo result
 */
function calculateGeometry(p) {
  if (typeof gearGeometry !== 'function')
    throw new Error('Không tìm thấy gearGeometry(). Kiểm tra formulas.js.');
  return gearGeometry(p.m, p.z1, p.z2, p.aw, p.psi_a, p.x1, p.x2);
}

// ─────────────────────────────────────────────────────────────
// 5. CALCULATE FORCES  –  Gọi tính lực
// ─────────────────────────────────────────────────────────────

/**
 * Tính lực tác dụng lên bánh răng.
 * Đây là wrapper, công thức chi tiết nên ở formulas.js.
 *
 * @param {Object} p    params
 * @param {Object} geo  kết quả hình học
 * @returns {Object}    { Ft, Fr, v, KH, KF }
 */
function calculateForces(p, geo) {
  const { T1, n1v, d1v, KHb, KHa, KHv, KFb, KFa, KFv } = p;

  // Lực vòng  Ft = 2T/d₁  (T₁ theo N·mm, d₁ mm → Ft là N)
  const Ft = 2 * T1 / geo.d1;

  // Lực hướng tâm  Fr = Ft · tan(α)  (α = 20°)
  const Fr = Ft * Math.tan(20 * Math.PI / 180);

  // Vận tốc vòng  v = π·d₁_ref·n₁ / 60000
  const v = (Math.PI * d1v * n1v) / 60000;

  // Tổng hệ số tải trọng
  const KH = KHb * KHa * KHv;
  const KF = KFb * KFa * KFv;

  return {
    Ft: +Ft.toFixed(3),
    Fr: +Fr.toFixed(3),
    Fa: 0,   // Răng thẳng, β=0
    v:  +v.toFixed(3),
    KH: +KH.toFixed(4),
    KF: +KF.toFixed(4),
  };
}

// ─────────────────────────────────────────────────────────────
// 6. STRENGTH CHECK  –  Kiểm nghiệm bền
// ─────────────────────────────────────────────────────────────

/**
 * Điều phối toàn bộ quy trình kiểm nghiệm bền.
 * Gọi V1..V5 từ formulas.js / inline HTML.
 *
 * @param {Object} p      params
 * @param {Object} geo    kết quả hình học
 * @param {Object} forces kết quả lực
 * @returns {Object}      strength result
 */
function checkStrength(p, geo, forces) {
  if (typeof V1 !== 'function' || typeof V3 !== 'function')
    throw new Error('Không tìm thấy hàm V1/V3. Kiểm tra formulas.js.');

  // Bước 1: Ứng suất cho phép
  const aH1 = V1(p.sHlim1, p.SH1, p.KHL1, p.sch1);
  const aH2 = V1(p.sHlim2, p.SH2, p.KHL2, p.sch2);
  const aF1 = V2(p.sFlim1, p.SF1, p.KFL1, p.sch1);
  const aF2 = V2(p.sFlim2, p.SF2, p.KFL2, p.sch2);

  const sHallow  = Math.min(aH1.sH, aH2.sH);
  const sHmax    = aH1.sHmax;
  const sF1allow = aF1.sF;
  const sF2allow = aF2.sF;
  const sF1max   = aF1.sFmax;
  const sF2max   = aF2.sFmax;

  // Bước 4: Kiểm nghiệm tiếp xúc
  const cont = V3(p.T1, geo.u, geo.d1, geo.bw, forces.KH, p.capVL, geo.eps_alpha, sHallow, p.x1 + p.x2);

  // Bước 5: Kiểm nghiệm uốn
  const bend = V4(p.T1, p.m, geo.d1, geo.bw, forces.KF, p.z1, p.z2, geo.eps_alpha, sF1allow, sF2allow);

  // Bước 6: Kiểm nghiệm quá tải
  const over = V5(p.Kqt, cont.sigH, bend.sF1, bend.sF2, sHallow, sHmax, sF1max, sF2max);

  // Điều kiện ăn khớp
  const uReal  = geo.u;
  const uErr   = Math.abs(uReal - p.u_yc) / p.u_yc * 100;
  const bwm    = +(geo.bw / p.m).toFixed(2);

  const meshOk = {
    z1: p.z1 >= 17,
    z2: p.z2 >= 17,
    eps: geo.eps_alpha >= 1.2,
    bwm: bwm >= 8 && bwm <= 30,
    uErr: uErr < 5,
  };

  const allOk = cont.ok && bend.ok1 && bend.ok2
    && over.okH && over.okF1 && over.okF2
    && meshOk.z1 && meshOk.z2 && meshOk.eps && meshOk.bwm;

  return {
    aH1, aH2, aF1, aF2,
    sHallow, sHmax, sF1allow, sF2allow, sF1max, sF2max,
    cont, bend, over,
    meshOk, bwm, uErr,
    allOk,
    KH: forces.KH,
    KF: forces.KF,
  };
}

// ─────────────────────────────────────────────────────────────
// 7. UPDATE RESULT UI  –  Cập nhật giao diện kết quả
// ─────────────────────────────────────────────────────────────

/** Gán textContent an toàn */
function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

/**
 * Cập nhật bảng kiểm tra nhanh (quick-check panel bên phải).
 *
 * @param {Object} p   params
 * @param {Object} S   strength result
 */
function updateCheckPanel(p, S) {
  // Helper nội bộ
  function setChk(valId, stateId, displayVal, ok) {
    setText(valId, displayVal);
    const el = document.getElementById(stateId);
    if (!el) return;
    el.className = `check-state ${ok ? 'cs-pass' : 'cs-fail'}`;
    el.textContent = ok ? 'ĐẠT ✓' : 'KHÔNG ĐẠT ✗';
  }

  setChk('ck_z1v', 'ck_z1s', String(p.z1), S.meshOk.z1);
  setChk('ck_z2v', 'ck_z2s', String(p.z2), S.meshOk.z2);
  setChk('ck_epsv', 'ck_epss', S.cont.Ze !== undefined ? S.cont.sigH.toFixed(2) : '—', S.meshOk.eps);

  // Trùng khớp
  const epsEl = document.getElementById('ck_epsv');
  if (epsEl) epsEl.textContent = '—'; // sẽ fill từ geo
  const epsState = document.getElementById('ck_epss');
  if (epsState) {
    epsState.className = `check-state ${S.meshOk.eps ? 'cs-pass' : 'cs-fail'}`;
    epsState.textContent = S.meshOk.eps ? 'ĐẠT ✓' : 'KHÔNG ĐẠT ✗';
  }

  setChk('ck_bwmv', 'ck_bwms', S.bwm.toFixed(2), S.meshOk.bwm);

  setText('ck_sHlim',     `≤ ${S.sHallow.toFixed(1)} MPa`);
  setText('ck_sF1lim',    `≤ ${S.sF1allow.toFixed(1)} MPa`);
  setText('ck_sF2lim',    `≤ ${S.sF2allow.toFixed(1)} MPa`);
  setText('ck_sHmax_lim', `≤ ${S.sHmax.toFixed(0)} MPa`);

  setChk('ck_sHv',  'ck_sHs',  `${S.cont.sigH.toFixed(2)} MPa`, S.cont.ok);
  setChk('ck_sF1v', 'ck_sF1s', `${S.bend.sF1.toFixed(2)} MPa`,  S.bend.ok1);
  setChk('ck_sF2v', 'ck_sF2s', `${S.bend.sF2.toFixed(2)} MPa`,  S.bend.ok2);
  setChk('ck_sHmv', 'ck_sHms', `${S.over.sHm.toFixed(2)} MPa`,  S.over.okH);
}

/**
 * Xây dựng 6 bảng kết quả chi tiết trong output section.
 * Logic nội dung giữ ở HTML engine (rowHdr, row2s…).
 * Controller chỉ cung cấp dữ liệu, gọi builder nếu tồn tại.
 *
 * Nếu formulas.js tách riêng builder, gọi builder ở đây.
 * Hiện tại builder inline → gọi lại runCalc() của engine HTML
 * chỉ sau khi controller tính xong và lưu.
 *
 * @param {Object} p       params
 * @param {Object} geo     kết quả hình học
 * @param {Object} forces  kết quả lực
 * @param {Object} S       strength result
 */
function updateResultUI(p, geo, forces, S) {
  // ── Quick check panel ──────────────────────────────────────
  updateCheckPanel(p, S);

  // ── Bảng 1: Ứng suất cho phép ──────────────────────────────
  if (typeof buildStressTable === 'function') {
    buildStressTable(p, S);
  } else {
    _buildStressTable(p, S);
  }

  // ── Bảng 2: Hình học ────────────────────────────────────────
  if (typeof buildGeoTable === 'function') {
    buildGeoTable(p, geo);
  } else {
    _buildGeoTable(p, geo);
  }

  // ── Bảng 3: Điều kiện ăn khớp ──────────────────────────────
  if (typeof buildMeshTable === 'function') {
    buildMeshTable(p, geo, forces, S);
  } else {
    _buildMeshTable(p, geo, forces, S);
  }

  // ── Bảng 4: Tiếp xúc ────────────────────────────────────────
  if (typeof buildContactTable === 'function') {
    buildContactTable(p, geo, forces, S);
  } else {
    _buildContactTable(p, geo, forces, S);
  }

  // ── Bảng 5: Uốn ─────────────────────────────────────────────
  if (typeof buildBendingTable === 'function') {
    buildBendingTable(p, geo, forces, S);
  } else {
    _buildBendingTable(p, geo, forces, S);
  }

  // ── Bảng 6: Quá tải ─────────────────────────────────────────
  if (typeof buildOverloadTable === 'function') {
    buildOverloadTable(p, S);
  } else {
    _buildOverloadTable(p, S);
  }

  // ── Verdict ─────────────────────────────────────────────────
  _buildVerdict(S);

  // ── Gear visual ─────────────────────────────────────────────
  if (typeof updateGearVisual === 'function') updateGearVisual();

  // ── Hiện output section, scroll vào ─────────────────────────
  const outSec = document.getElementById('outputSection');
  if (outSec) {
    outSec.style.display = 'block';
    setTimeout(() => outSec.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);
  }
}

// ─── Fallback builders (dùng khi formulas.js không có builder riêng) ───

const _f2 = v => (typeof v === 'number' ? v.toFixed(2) : String(v));
const _f3 = v => (typeof v === 'number' ? v.toFixed(3) : String(v));
const _f4 = v => (typeof v === 'number' ? v.toFixed(4) : String(v));

function _chkTag(ok) {
  return `<span class="check-tag ${ok ? 'pass' : 'fail'}">${ok ? 'ĐẠT ✓' : 'KHÔNG ĐẠT ✗'}</span>`;
}
function _marginBadge(val, limit, ok) {
  const pct = Math.abs((val / limit - 1) * 100).toFixed(1);
  const cls  = ok ? 'margin-ok' : 'margin-bad';
  return `<span class="margin-badge ${cls}">${ok ? `DP ${pct}%` : `Vượt ${pct}%`}</span>`;
}

function _rowHdr(label) {
  return `<tr class="r-section-hdr"><td colspan="10">${label}</td></tr>`;
}
function _row2s(name, sym, v1, v2, unit, bold = false) {
  const s = bold ? 'font-weight:700;' : '';
  return `<tr>
    <td><div class="r-param" style="${s}">${name}</div></td>
    <td class="r-unit" style="color:var(--cyan);font-weight:600;">${sym}</td>
    <td class="r-val">${_f3(v1)}</td>
    <td class="r-val teal">${_f3(v2)}</td>
    <td class="r-unit">${unit}</td></tr>`;
}
function _rowGeo(name, sym, v1, v2, unit, bold = false) {
  const s = bold ? 'font-weight:700;' : '';
  const fv = v => typeof v === 'number' ? v.toFixed(v % 1 === 0 && v < 1000 ? 0 : 3) : v;
  return `<tr>
    <td><div class="r-param" style="${s}">${name}</div></td>
    <td class="r-unit" style="color:var(--cyan);font-weight:600;text-align:center;">${sym}</td>
    <td class="r-val">${fv(v1)}</td>
    <td class="r-val teal">${fv(v2)}</td>
    <td class="r-unit">${unit}</td></tr>`;
}
function _rowMesh(name, sym, val, unit, ok, display) {
  return `<tr>
    <td><div class="r-param">${name}</div></td>
    <td class="r-unit" style="color:var(--cyan);font-weight:600;text-align:center;">${sym}</td>
    <td class="r-val">${display ?? _f4(val)}</td>
    <td class="r-unit">${unit}</td>
    <td class="r-status">${_chkTag(ok)}</td></tr>`;
}
function _rowOL(name, sym, val, limit, unit, ok) {
  return `<tr>
    <td><div class="r-param"><span class="r-symbol">${sym}</span>${name}</div></td>
    <td class="r-unit" style="color:var(--cyan);font-weight:600;">${sym}</td>
    <td class="r-val">${_f3(val)}</td>
    <td class="r-val teal">${_f3(limit)}</td>
    <td class="r-unit">${unit}</td>
    <td class="r-status">${_chkTag(ok)} ${_marginBadge(val, limit, ok)}</td></tr>`;
}

function _buildStressTable(p, S) {
  const el = document.getElementById('tblStress');
  if (!el) return;
  el.innerHTML = `
    ${_rowHdr('Ứng suất tiếp xúc cho phép')}
    ${_row2s('Giới hạn mỏi tiếp xúc', 'σ°Hlim', p.sHlim1, p.sHlim2, 'MPa')}
    ${_row2s('Hệ số an toàn tiếp xúc',  'SH',     p.SH1,   p.SH2,   '—')}
    ${_row2s('Hệ số tuổi thọ tiếp xúc', 'KHL',    p.KHL1,  p.KHL2,  '—')}
    ${_row2s('[σH] = σ°Hlim·KHL/SH',   '[σH]',  S.aH1.sH, S.aH2.sH,'MPa', true)}
    <tr>
      <td><div class="r-param" style="font-weight:700;">[σH] bộ truyền = min([σH]₁, [σH]₂)</div></td>
      <td class="r-unit" style="color:var(--cyan);font-weight:600;">[σH]</td>
      <td class="r-val" colspan="2" style="font-size:16px;">${S.sHallow.toFixed(3)}</td>
      <td class="r-unit">MPa</td></tr>
    <tr>
      <td><div class="r-param">[σH]max = 2.8·σch₁</div></td>
      <td class="r-unit" style="color:var(--cyan);font-weight:600;">[σH]max</td>
      <td class="r-val">${S.sHmax.toFixed(3)}</td>
      <td class="r-val teal">—</td>
      <td class="r-unit">MPa</td></tr>
    ${_rowHdr('Ứng suất uốn cho phép')}
    ${_row2s('Giới hạn mỏi uốn', 'σ°Flim', p.sFlim1, p.sFlim2, 'MPa')}
    ${_row2s('Hệ số an toàn uốn', 'SF',    p.SF1,   p.SF2,   '—')}
    ${_row2s('Hệ số tuổi thọ uốn','KFL',   p.KFL1,  p.KFL2,  '—')}
    ${_row2s('[σF] = σ°Flim·KFL/SF','[σF]', S.aF1.sF, S.aF2.sF,'MPa', true)}
    ${_row2s('[σF]max = 0.8·σch', '[σF]max',S.sF1max, S.sF2max,'MPa')}`;
}

function _buildGeoTable(p, geo) {
  const el = document.getElementById('tblGeo');
  if (!el) return;
  el.innerHTML = `
    ${_rowHdr('Thông số cơ bản')}
    ${_rowGeo('Môđun pháp','m', p.m, p.m,'mm')}
    ${_rowGeo('Khoảng cách trục','aw', p.aw, p.aw,'mm')}
    ${_rowGeo('Chiều rộng vành răng = ψa·aw','bw', geo.bw, geo.bw,'mm', true)}
    ${_rowGeo('Tỉ số truyền thực u = z₂/z₁','u', geo.u, geo.u,'—')}
    ${_rowGeo('Số răng','z', p.z1, p.z2,'răng', true)}
    ${_rowGeo('Hệ số dịch chỉnh','x', p.x1, p.x2,'—')}
    ${_rowGeo('Hệ số trùng khớp ngang εα','εα', geo.eps_alpha,'—','—')}
    ${_rowGeo('Hệ số hình dạng bề mặt tx','ZH', geo.ZH,'—','—')}
    ${_rowHdr('Đường kính các vòng')}
    ${_rowGeo('Vòng chia d = m·z','d', geo.d1, geo.d2,'mm', true)}
    ${_rowGeo('Vòng lăn dw','dw', geo.dw1, geo.dw2,'mm')}
    ${_rowGeo('Đỉnh răng da = d+2(1+x)m','da', geo.da1, geo.da2,'mm')}
    ${_rowGeo('Đáy răng df = d−(2.5−2x)m','df', geo.df1, geo.df2,'mm')}
    ${_rowHdr('Hình dạng răng')}
    ${_rowGeo('Chiều cao đầu răng ha','ha', geo.ha, geo.ha,'mm')}
    ${_rowGeo('Chiều cao chân răng hf','hf', geo.hf, geo.hf,'mm')}
    ${_rowGeo('Chiều cao toàn phần h','h',  geo.h,  geo.h, 'mm')}
    ${_rowGeo('Khe hở hướng tâm c = 0.25m','c', geo.c, geo.c,'mm')}
    ${_rowGeo('Bước răng p = π·m','p', geo.p, geo.p,'mm')}
    ${_rowGeo('Bước cơ sở pb = p·cosα','pb', geo.pb, geo.pb,'mm')}
    ${_rowGeo('Hệ số dạng răng YF (Bảng 6.7)','YF', geo.YF1, geo.YF2,'—', true)}`;
}

function _buildMeshTable(p, geo, forces, S) {
  const el = document.getElementById('tblMesh');
  if (!el) return;
  const bwm = S.bwm;
  const uErr = S.uErr;
  el.innerHTML = `
    ${_rowMesh('Số răng bánh nhỏ ≥ 17','z₁', p.z1,'răng', S.meshOk.z1, String(p.z1))}
    ${_rowMesh('Số răng bánh lớn ≥ 17','z₂', p.z2,'răng', S.meshOk.z2, String(p.z2))}
    ${_rowMesh('Hệ số trùng khớp ≥ 1.2','εα', geo.eps_alpha,'—', S.meshOk.eps, geo.eps_alpha.toFixed(4))}
    ${_rowMesh('Tỷ lệ bw/m ∈ [8, 30]','bw/m', bwm,'—', S.meshOk.bwm, bwm.toFixed(2))}
    ${_rowMesh('Sai lệch tỉ số truyền < 5%','Δu%', uErr,'%', S.meshOk.uErr, uErr.toFixed(2)+'%')}
    ${_rowMesh('Vận tốc vòng v = π·d₁·n₁/60000','v', forces.v,'m/s', true, forces.v+' m/s')}`;
}

function _buildContactTable(p, geo, forces, S) {
  const el = document.getElementById('tblContact');
  if (!el) return;
  const { cont, sHallow } = S;
  el.innerHTML = `
    ${_rowHdr('Hệ số và thông số trung gian')}
    <tr><td><div class="r-param">Hệ số cơ tính vật liệu ZM</div></td>
      <td class="r-unit" style="color:var(--cyan);font-weight:600;">ZM</td>
      <td class="r-val">${cont.ZM.toFixed(0)}</td><td class="r-unit">MPa^0.5</td></tr>
    <tr><td><div class="r-param">Hệ số hình dạng bề mặt tx (Bảng 6.12)</div></td>
      <td class="r-unit" style="color:var(--cyan);font-weight:600;">ZH</td>
      <td class="r-val">${cont.ZH.toFixed(4)}</td><td class="r-unit">—</td></tr>
    <tr><td><div class="r-param">Hệ số trùng khớp Zε = √((4−εα)/3)</div></td>
      <td class="r-unit" style="color:var(--cyan);font-weight:600;">Zε</td>
      <td class="r-val">${cont.Ze.toFixed(4)}</td><td class="r-unit">—</td></tr>
    <tr><td><div class="r-param">Tổng hệ số tải trọng KH = KHβ·KHα·KHv</div></td>
      <td class="r-unit" style="color:var(--cyan);font-weight:600;">KH</td>
      <td class="r-val">${forces.KH.toFixed(4)}</td><td class="r-unit">—</td></tr>
    ${_rowHdr('Kết quả kiểm nghiệm')}
    <tr>
      <td><div class="r-param" style="font-weight:700;">Ứng suất tiếp xúc tính được</div></td>
      <td class="r-unit" style="color:var(--cyan);font-weight:600;">σH</td>
      <td class="r-val" style="font-size:17px;color:${cont.ok ? 'var(--green)' : 'var(--red)'};">${cont.sigH.toFixed(2)}</td>
      <td class="r-unit">MPa</td></tr>
    <tr>
      <td><div class="r-param">Ứng suất tiếp xúc cho phép [σH]</div></td>
      <td class="r-unit" style="color:var(--cyan);font-weight:600;">[σH]</td>
      <td class="r-val teal">${sHallow.toFixed(2)}</td>
      <td class="r-unit">MPa</td></tr>
    <tr>
      <td colspan="2" style="padding:10px 18px;">${_chkTag(cont.ok)} ${_marginBadge(cont.sigH, sHallow, cont.ok)}</td>
      <td colspan="2"></td></tr>`;
}

function _buildBendingTable(p, geo, forces, S) {
  const el = document.getElementById('tblBending');
  if (!el) return;
  const { bend, sF1allow, sF2allow } = S;
  el.innerHTML = `
    ${_rowHdr('Hệ số và thông số trung gian')}
    <tr><td><div class="r-param">Hệ số dạng răng bánh nhỏ (Bảng 6.7)</div></td>
      <td class="r-unit" style="color:var(--cyan);font-weight:600;">YF₁</td>
      <td class="r-val">${bend.YF1.toFixed(3)}</td><td class="r-unit">—</td></tr>
    <tr><td><div class="r-param">Hệ số dạng răng bánh lớn (Bảng 6.7)</div></td>
      <td class="r-unit" style="color:var(--cyan);font-weight:600;">YF₂</td>
      <td class="r-val">${bend.YF2.toFixed(3)}</td><td class="r-unit">—</td></tr>
    <tr><td><div class="r-param">Hệ số trùng khớp Yε = 1/εα</div></td>
      <td class="r-unit" style="color:var(--cyan);font-weight:600;">Yε</td>
      <td class="r-val">${bend.Ye.toFixed(4)}</td><td class="r-unit">—</td></tr>
    <tr><td><div class="r-param">Hệ số nghiêng răng (β=0°)</div></td>
      <td class="r-unit" style="color:var(--cyan);font-weight:600;">Yβ</td>
      <td class="r-val">${bend.Yb.toFixed(1)}</td><td class="r-unit">—</td></tr>
    <tr><td><div class="r-param">Tổng hệ số tải trọng KF = KFβ·KFα·KFv</div></td>
      <td class="r-unit" style="color:var(--cyan);font-weight:600;">KF</td>
      <td class="r-val">${forces.KF.toFixed(4)}</td><td class="r-unit">—</td></tr>
    ${_rowHdr('Kết quả')}
    <tr>
      <td><div class="r-param" style="font-weight:700;">Ứng suất uốn bánh nhỏ</div></td>
      <td class="r-unit" style="color:var(--cyan);font-weight:600;">σF₁</td>
      <td class="r-val" style="font-size:16px;color:${bend.ok1 ? 'var(--green)' : 'var(--red)'};">${bend.sF1.toFixed(2)}</td>
      <td class="r-unit">MPa</td></tr>
    <tr>
      <td><div class="r-param">Ứng suất uốn cho phép bánh nhỏ [σF]₁</div></td>
      <td class="r-unit" style="color:var(--cyan);font-weight:600;">[σF]₁</td>
      <td class="r-val teal">${sF1allow.toFixed(2)}</td>
      <td class="r-unit">MPa</td></tr>
    <tr>
      <td colspan="2" style="padding:8px 18px;">${_chkTag(bend.ok1)} ${_marginBadge(bend.sF1, sF1allow, bend.ok1)}</td>
      <td colspan="2"></td></tr>
    <tr>
      <td><div class="r-param" style="font-weight:700;">Ứng suất uốn bánh lớn</div></td>
      <td class="r-unit" style="color:var(--cyan);font-weight:600;">σF₂</td>
      <td class="r-val" style="font-size:16px;color:${bend.ok2 ? 'var(--green)' : 'var(--red)'};">${bend.sF2.toFixed(2)}</td>
      <td class="r-unit">MPa</td></tr>
    <tr>
      <td><div class="r-param">Ứng suất uốn cho phép bánh lớn [σF]₂</div></td>
      <td class="r-unit" style="color:var(--cyan);font-weight:600;">[σF]₂</td>
      <td class="r-val teal">${sF2allow.toFixed(2)}</td>
      <td class="r-unit">MPa</td></tr>
    <tr>
      <td colspan="2" style="padding:8px 18px;">${_chkTag(bend.ok2)} ${_marginBadge(bend.sF2, sF2allow, bend.ok2)}</td>
      <td colspan="2"></td></tr>`;
}

function _buildOverloadTable(p, S) {
  const el = document.getElementById('tblOverload');
  if (!el) return;
  const { over, sHmax, sF1max, sF2max } = S;
  el.innerHTML = `
    <tr>
      <td><div class="r-param">Hệ số quá tải</div></td>
      <td class="r-unit" style="color:var(--cyan);font-weight:600;">Kqt</td>
      <td class="r-val">${p.Kqt.toFixed(2)}</td>
      <td class="r-val teal">—</td><td class="r-unit">T_max/T</td><td></td></tr>
    <tr>
      <td><div class="r-param">√Kqt</div></td>
      <td class="r-unit" style="color:var(--cyan);font-weight:600;">√Kqt</td>
      <td class="r-val">${over.sqK}</td>
      <td class="r-val teal">—</td><td class="r-unit">—</td><td></td></tr>
    ${_rowOL('Tiếp xúc quá tải = [σH]·√Kqt','σH_max',  over.sHm,  sHmax,  'MPa', over.okH)}
    ${_rowOL('Uốn quá tải bánh nhỏ = σF₁·√Kqt','σF₁_max',over.sF1m, sF1max, 'MPa', over.okF1)}
    ${_rowOL('Uốn quá tải bánh lớn = σF₂·√Kqt','σF₂_max',over.sF2m, sF2max, 'MPa', over.okF2)}`;
}

function _buildVerdict(S) {
  const el = document.getElementById('verdictBox');
  if (!el) return;
  if (S.allOk) {
    el.className = 'verdict-box verdict-pass';
    el.innerHTML = `<span style="font-size:26px;">✅</span>
      <div>
        <div style="font-size:16px;font-weight:800;">BỘ TRUYỀN ĐẠT YÊU CẦU</div>
        <div style="font-size:12px;font-weight:400;color:var(--tx2);margin-top:4px;">
          Tất cả điều kiện bền tiếp xúc, uốn và quá tải đều thỏa mãn.
        </div>
      </div>`;
  } else {
    const fails = buildFailList(S);
    el.className = 'verdict-box verdict-fail';
    el.innerHTML = `<span style="font-size:26px;">⛔</span>
      <div>
        <div style="font-size:16px;font-weight:800;">BỘ TRUYỀN CHƯA ĐẠT</div>
        <div style="font-size:12px;font-weight:400;color:var(--tx2);margin-top:4px;">
          Chưa đạt: ${fails.join(', ')} — Điều chỉnh m, z, bw hoặc thay đổi vật liệu.
        </div>
      </div>`;
  }
}

// ─────────────────────────────────────────────────────────────
// 8. SAVE MODULE DATA  –  Lưu M4_Data
// ─────────────────────────────────────────────────────────────

/**
 * Đóng gói và lưu kết quả M4 vào storage.
 * Đây là điểm cuối cùng của pipeline M1→M4.
 *
 * @param {Object} p       params
 * @param {Object} geo     kết quả hình học
 * @param {Object} forces  kết quả lực
 * @param {Object} S       strength result
 * @returns {Object}       M4_Data đã lưu
 */
function saveM4Data(p, geo, forces, S) {
  const M4_Data = {
    // ── Thông số truyền động ──────────────────────────────────
    P4:      p.T1 * p.n1v / 9550000,  // kW (gần đúng)
    n4:      p.n1v / geo.u,            // rpm trục ra
    T1:      p.T1,
    n1:      p.n1v,

    // ── Tỉ số truyền ─────────────────────────────────────────
    i_tru:   geo.u,

    // ── Số răng ──────────────────────────────────────────────
    z1:      p.z1,
    z2:      p.z2,

    // ── Hình học ─────────────────────────────────────────────
    m:       p.m,
    aw:      p.aw,
    bw:      geo.bw,
    x1:      p.x1,
    x2:      p.x2,

    d1:      geo.d1,
    d2:      geo.d2,
    dw1:     geo.dw1,
    dw2:     geo.dw2,
    da1:     geo.da1,
    da2:     geo.da2,
    df1:     geo.df1,
    df2:     geo.df2,
    ha:      geo.ha,
    hf:      geo.hf,
    h:       geo.h,

    // ── Lực tác dụng ─────────────────────────────────────────
    Ft:      forces.Ft,
    Fr:      forces.Fr,
    Fa:      forces.Fa,
    v:       forces.v,

    // ── Kiểm nghiệm bền ──────────────────────────────────────
    sigmaH:  S.cont.sigH,
    sigmaF1: S.bend.sF1,
    sigmaF2: S.bend.sF2,

    sHallow:  S.sHallow,
    sF1allow: S.sF1allow,
    sF2allow: S.sF2allow,

    // ── Trạng thái ───────────────────────────────────────────
    allOk:   S.allOk,
    status:  S.allOk ? 'Đạt' : 'Không đạt',

    // ── Meta ─────────────────────────────────────────────────
    calculatedAt: new Date().toISOString(),
  };

  try {
    if (typeof saveData === 'function') {
      saveData(M4_KEY, M4_Data);
    } else {
      localStorage.setItem(M4_KEY, JSON.stringify(M4_Data));
    }
    console.info('[M4] Đã lưu M4_Data:', M4_Data);
  } catch (err) {
    console.error('[M4] Lỗi lưu M4_Data:', err);
    showToast('error', '⚠️ Không thể lưu M4_Data vào storage!');
  }

  return M4_Data;
}

// ─────────────────────────────────────────────────────────────
// 9. EXPORT REPORT  –  Tổng hợp hệ thống M1→M4
// ─────────────────────────────────────────────────────────────

/**
 * Đọc dữ liệu từ tất cả module và tổng hợp báo cáo hệ thống.
 * M4 là module cuối — nó tổng hợp toàn bộ dẫn động.
 *
 * @returns {Object|null}  system summary hoặc null nếu thiếu data
 */
function buildSystemReport() {
  const keys = ['M1_Data', 'M2_Data', M3_KEY, M4_KEY];
  const modules = {};

  keys.forEach(k => {
    try {
      const raw = (typeof loadData === 'function')
        ? loadData(k)
        : JSON.parse(localStorage.getItem(k) || 'null');
      modules[k] = raw;
    } catch {
      modules[k] = null;
    }
  });

  const missing = keys.filter(k => !modules[k]);
  if (missing.length > 0) {
    console.warn('[M4] Báo cáo tổng hợp thiếu:', missing.join(', '));
    return null;
  }

  return {
    M1: modules['M1_Data'],
    M2: modules['M2_Data'],
    M3: modules[M3_KEY],
    M4: modules[M4_KEY],
    generatedAt: new Date().toISOString(),
    allModulesPassed:
      modules[M3_KEY]?.dat_all &&
      modules[M4_KEY]?.allOk,
  };
}

/**
 * Kích hoạt xuất báo cáo — gọi workflow.js nếu có, fallback console.
 */
function exportSystemReport() {
  const report = buildSystemReport();

  if (!report) {
    showToast('error', '❌ Chưa đủ dữ liệu từ tất cả module (M1→M4) để xuất báo cáo.');
    return;
  }

  if (typeof exportReport === 'function') {
    exportReport(report);
    return;
  }

  // Fallback: download JSON
  const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href     = url;
  a.download = `MechaMix_BaoCaoHeThong_${new Date().toISOString().slice(0, 10)}.json`;
  a.click();
  URL.revokeObjectURL(url);

  showToast('ok', '📄 Đã xuất báo cáo hệ thống (JSON). Tích hợp workflow.js để xuất PDF/Word.');
  console.info('[M4] System Report:', report);
}

// ─────────────────────────────────────────────────────────────
// PUBLIC API  –  Hàm gọi từ HTML onclick
// ─────────────────────────────────────────────────────────────

/**
 * runCalc()  —  Gọi từ nút "Chạy tính toán đầy đủ"
 * Pipeline hoàn chỉnh của Module 4.
 */
function runCalc() {
  // 3. Đọc input
  const { params, errors } = readInput();

  if (errors.length > 0) {
    showToast('error', `❌ Thiếu hoặc sai định dạng: ${errors.join(', ')}`);
    return;
  }

  // Validate logic nhẹ
  const warns = validateParams(params);
  warns.forEach(w => showToast('warn', `⚠️ ${w}`));

  // Kiểm tra z tối thiểu sớm
  const Z_MIN = 17;
  if (params.z1 < Z_MIN || params.z2 < Z_MIN) {
    showToast('error', '⚠️ z₁, z₂ phải ≥ 17 (z_min tránh cắt chân răng)');
    return;
  }
  if (params.m <= 0 || params.aw <= 0) {
    showToast('error', '⚠️ Kiểm tra lại m và a_w — phải > 0');
    return;
  }
  if (params.T1 <= 0) {
    showToast('error', '⚠️ T₁ phải > 0');
    return;
  }

  try {
    // 4. Tính hình học
    const geo = calculateGeometry(params);

    // 5. Tính lực
    const forces = calculateForces(params, geo);

    // 6. Kiểm nghiệm bền
    const S = checkStrength(params, geo, forces);

    // 7. Cập nhật UI
    updateResultUI(params, geo, forces, S);

    // 8. Lưu dữ liệu
    const M4 = saveM4Data(params, geo, forces, S);

    // Toast tổng kết
    if (S.allOk) {
      showToast('ok', '✅ Tính toán hoàn tất — Bộ truyền đạt tất cả điều kiện bền!');
    } else {
      const fails = buildFailList(S);
      showToast('error', `⛔ Chưa đạt: ${fails.join(', ')} — Xem bảng kết quả để điều chỉnh.`);
    }

    console.info('[M4] Pipeline hoàn tất.', { params, geo, forces, S, M4 });

  } catch (err) {
    showToast('error', `❌ Lỗi tính toán: ${err.message}`);
    console.error('[M4] Lỗi:', err);
  }
}

/**
 * resetForm()  —  Gọi từ nút "Reset"
 */
function resetForm() {
  // Ẩn output section
  const outSec = document.getElementById('outputSection');
  if (outSec) outSec.style.display = 'none';

  // Reset badge kiểm tra nhanh
  CHECK_STATE_IDS.forEach(id => {
    const el = document.getElementById(id);
    if (el) { el.className = 'check-state cs-idle'; el.textContent = '—'; }
  });
  CHECK_VAL_IDS.forEach(id => setText(id, '—'));
  CHECK_LIM_IDS.forEach(id => setText(id, '—'));

  // Cập nhật lại gear visual với giá trị form hiện tại
  if (typeof updateGearVisual === 'function') updateGearVisual();

  showToast('ok', '🔄 Đã reset — Nhập lại thông số và chạy tính toán mới.');
}

// ─────────────────────────────────────────────────────────────
// HELPER NỘI BỘ
// ─────────────────────────────────────────────────────────────

/** Tổng hợp điều kiện không đạt từ strength result */
function buildFailList(S) {
  const fails = [];
  if (!S.meshOk.z1)  fails.push('z₁ < 17');
  if (!S.meshOk.z2)  fails.push('z₂ < 17');
  if (!S.meshOk.eps) fails.push('εα < 1.2');
  if (!S.meshOk.bwm) fails.push('bw/m ngoài [8,30]');
  if (!S.cont.ok)    fails.push('σH tiếp xúc');
  if (!S.bend.ok1)   fails.push('σF1 uốn');
  if (!S.bend.ok2)   fails.push('σF2 uốn');
  if (!S.over.okH)   fails.push('σH_max quá tải');
  if (!S.over.okF1)  fails.push('σF1_max quá tải');
  if (!S.over.okF2)  fails.push('σF2_max quá tải');
  return fails;
}

/**
 * showToast()  —  Hiển thị thông báo toast
 * Dùng engine có sẵn trong HTML, fallback console nếu không có.
 *
 * @param {'ok'|'error'|'warn'} type
 * @param {string} msg
 */
function showToast(type, msg) {
  const wrap = document.getElementById('toastWrap');
  if (!wrap) {
    console[type === 'error' ? 'error' : 'info']('[M4 Toast]', msg);
    return;
  }
  const icons = { ok: '✅', error: '❌', warn: '⚠️' };
  const t = document.createElement('div');
  t.className = `toast toast-${type}`;
  t.innerHTML = `
    <span style="font-size:18px;">${icons[type] ?? 'ℹ️'}</span>
    <span class="toast-msg">${msg}</span>
    <span class="toast-close" onclick="this.parentElement.remove()">✕</span>`;
  wrap.appendChild(t);
  setTimeout(() => {
    t.style.opacity   = '0';
    t.style.transform = 'translateX(20px)';
    t.style.transition = 'all 0.3s';
    setTimeout(() => t.remove(), 300);
  }, 5500);
}

// ─────────────────────────────────────────────────────────────
// ENTRY POINT  –  Tự động chạy khi DOM sẵn sàng
// ─────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  console.info('[M4] BanhRangTru module khởi động.');

  // 1. Đọc M3
  const m3 = loadM3Data(false);  // false = không force redirect

  // 2. Init UI
  initUI(m3);

  // Live preview: cập nhật gear visual khi thay đổi input
  ['m', 'z1', 'z2', 'aw'].forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    el.addEventListener('input',  () => { if (typeof updateGearVisual === 'function') updateGearVisual(); });
    el.addEventListener('change', () => { if (typeof updateGearVisual === 'function') updateGearVisual(); });
  });

  // Nút xuất báo cáo (nếu có trong HTML)
  const btnExport = document.getElementById('btnExportReport');
  if (btnExport) {
    btnExport.addEventListener('click', exportSystemReport);
  }

  console.info('[M4] Khởi tạo hoàn tất. Sẵn sàng nhận thông số.');
});
