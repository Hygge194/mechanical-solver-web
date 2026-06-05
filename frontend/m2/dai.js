/**
 * MechaMix – m2/dai.js
 * Orchestrator cho Module 2 – Bộ truyền đai hình thang
 *
 * Luồng:
 *   localStorage.M1 → prefill form → tinhDai() (nội bộ) || API fallback
 *                   → render UI → save localStorage.M2 → goToM3()
 */

"use strict";

/* ══════════════════════════════════════════════════════════════
   0. CONSTANTS
══════════════════════════════════════════════════════════════ */
const URL_BELT = "http://127.0.0.1:8000/api/v1/calculate/belt";

/* ══════════════════════════════════════════════════════════════
   1. LOAD DỮ LIỆU TỪ M1
══════════════════════════════════════════════════════════════ */

/**
 * Đọc dữ liệu M1 từ localStorage và trả về object đã được normalize.
 * @returns {{ ok: boolean, data?: object, error?: string }}
 */
function loadM1() {
    const m1 = loadModuleData(STORAGE_KEYS.M1);

    if (!m1) {
        return {
            ok: false,
            error: "Chưa có dữ liệu Module 1 — hãy hoàn thành M1 trước.",
        };
    }

    // Kiểm tra các trường bắt buộc
    const missing = [];
    if (!m1.kinematics)       missing.push("kinematics");
    if (!m1.ratios)           missing.push("ratios");
    if (!m1.power)            missing.push("power");
    if (!m1.input)            missing.push("input");

    if (missing.length) {
        return {
            ok: false,
            error: `Dữ liệu M1 thiếu các trường: ${missing.join(", ")}. Vui lòng chạy lại M1.`,
        };
    }

    return { ok: true, data: m1 };
}

/* ══════════════════════════════════════════════════════════════
   2. ĐIỀN DỮ LIỆU LÊN FORM (prefill)
══════════════════════════════════════════════════════════════ */

/**
 * Điền thông số từ M1 vào các input của Bước 1.
 * Nếu trường không tồn tại trong DOM thì bỏ qua (không throw).
 * @param {object} m1 – kết quả loadModuleData(STORAGE_KEYS.M1)
 */
function prefillFromM1(m1) {
    const kin = m1.kinematics;
    const ratios = m1.ratios;
    const input = m1.input;

    // Công suất làm việc P₁ = công suất trên trục động cơ
    setVal("inP1",
        kin.P_dc ?? kin.truc_dc?.P ?? m1.power?.pct ?? "");

    // Tốc độ trục động cơ n₁
    setVal("inN1",
        kin.n_dc ?? kin.truc_dc?.n ?? m1.motor?.speed ?? "");

    // Tỉ số truyền đai u_đ từ phân phối tỉ số
    setVal("inUd",
        ratios.u_dai ?? ratios.u_1 ?? "");

    // Tuổi thọ (nếu form có trường này)
    setVal("inLifetime", input.lifetime ?? "");

    showBanner(m1);
}

/**
 * Cập nhật banner "Dữ liệu từ M1" với thông tin động cơ đã chọn.
 */
function showBanner(m1) {
    const banner = document.querySelector(".m1-banner-text");
    if (!banner) return;

    const motor  = m1.motor  ? `<strong>${m1.motor.model ?? m1.motor.name ?? "—"}</strong>` : "—";
    const Pct    = m1.power?.pct != null ? m1.power.pct.toFixed(2) + " kW" : "—";
    const nDC    = m1.kinematics?.n_dc ?? m1.motor?.speed ?? "—";
    const uDai   = m1.ratios?.u_dai?.toFixed(2) ?? "—";

    banner.innerHTML =
        `Dữ liệu tự động nạp từ <strong>Module 1</strong>: ` +
        `Động cơ ${motor} · P₁ = ${Pct} · n₁ = ${nDC} v/ph · u_đ = ${uDai}. ` +
        `Bạn có thể chỉnh tay nếu cần kiểm tra phương án khác.`;
}

/* ══════════════════════════════════════════════════════════════
   3. XÂY DỰNG PAYLOAD & GỌI BACKEND (với fallback nội bộ)
══════════════════════════════════════════════════════════════ */

/**
 * Thu thập thông số từ form và trả về payload gửi API.
 * @returns {object} payload
 */
function buildPayload() {
    return {
        power:    parseFloat(document.getElementById("inP1")?.value  ?? 0),
        speed:    parseFloat(document.getElementById("inN1")?.value  ?? 0),
        ratio:    parseFloat(document.getElementById("inUd")?.value  ?? 0),
        slip:     parseFloat(document.getElementById("inEps")?.value ?? 0.02),
        load_factor: parseFloat(document.getElementById("inKd")?.value  ?? 1.2),
        belt_type:   document.getElementById("inLoai")?.value ?? "auto",
        lifetime: parseFloat(document.getElementById("inLifetime")?.value ?? 0) || null,
    };
}

/**
 * Gọi API backend.
 * Nếu backend không khả dụng (network error / 4xx / 5xx), ném Error để
 * caller chuyển sang fallback nội bộ.
 * @param {object} payload
 * @returns {Promise<object>} result từ backend
 */
async function callBeltAPI(payload) {
    const resp = await fetch(URL_BELT, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify(payload),
    });

    if (!resp.ok) {
        const body = await resp.text().catch(() => "");
        throw new Error(`API ${resp.status}: ${body.slice(0, 120)}`);
    }

    const json = await resp.json();

    // Backend trả về { status, data: {...} } — unwrap để dùng như runLocal()
    if (json.status !== "success") {
        throw new Error(`API trả về lỗi: ${json.detail ?? json.message ?? JSON.stringify(json)}`);
    }
    return { ...json.data, _source: "api" };
}

/**
 * Gọi hàm tinhDai() có sẵn trong dai.html và chuẩn hoá kết quả
 * thành cùng schema với API backend để phần render dùng chung.
 * @param {object} payload
 * @returns {object} result đã chuẩn hoá
 */
function runLocal(payload) {
    if (typeof tinhDai !== "function") {
        throw new Error("Không tìm thấy hàm tinhDai() — kiểm tra script trong HTML.");
    }

    const kq = tinhDai(
        payload.power,
        payload.speed,
        payload.ratio,
        payload.load_factor,
        payload.slip,
        payload.belt_type,
    );

    // Chuẩn hoá sang schema chung (khớp cả API lẫn nội bộ)
    return {
        belt_type: kq.loai,
        d1:        kq.d1,
        d2:        kq.d2,
        v:         kq.v,
        L:         kq.L,
        a:         kq.a,
        a_dc:      kq.adcS,
        alpha1:    kq.alpha1,
        u_actual:  kq.utt,
        delta_u:   kq.ss,
        Ca:        kq.Ca,
        Cl:        kq.Cl,
        Cu:        kq.Cu,
        Cz:        kq.Cz,
        Z:         kq.Z,
        B:         kq.B,
        da1:       kq.da1,
        da2:       kq.da2,
        F0:        kq.F0,
        Ft:        kq.Ft,
        Fr:        kq.Fr,
        Fv:        kq.Fv,
        P0:        kq.P0,
        // log nội bộ (chỉ có khi dùng fallback)
        _log:      kq.log ?? [],
        _warnings: kq.warnL ?? [],
        _source:   "local",
    };
}

/* ══════════════════════════════════════════════════════════════
   4. RENDER KẾT QUẢ LÊN UI
══════════════════════════════════════════════════════════════ */

/**
 * Ghi một giá trị số vào element; bỏ qua nếu element không tồn tại.
 * @param {string} id
 * @param {number|string} val
 * @param {string} [suffix]
 */
function fillOut(id, val, suffix = "") {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = val !== null && val !== undefined
        ? (typeof val === "number" ? val.toFixed(2) : val) + suffix
        : "—";
}

/**
 * Render toàn bộ kết quả lên các stat tiles, bảng, biểu đồ.
 * Hàm này CHỈ cập nhật DOM — không lưu storage, không gọi API.
 * @param {object} result – schema chuẩn từ runLocal() hoặc API
 */
function renderResult(result) {
    // ── Stat tiles (nếu có trên trang) ───────────────────────────────────
    fillOut("outBeltType", result.belt_type);
    fillOut("outD1",       result.d1,     " mm");
    fillOut("outD2",       result.d2,     " mm");
    fillOut("outV",        result.v,      " m/s");
    fillOut("outL",        result.L,      " mm");
    fillOut("outA",        result.a,      " mm");
    fillOut("outAlpha1",   result.alpha1, "°");
    fillOut("outZ",        result.Z,      " đai");
    fillOut("outB",        result.B,      " mm");
    fillOut("outDa1",      result.da1,    " mm");
    fillOut("outDa2",      result.da2,    " mm");
    fillOut("outF0",       result.F0,     " N");
    fillOut("outFt",       result.Ft,     " N");
    fillOut("outFr",       result.Fr,     " N");

    // Bảng kết quả chính (nếu dùng JS render thay vì HTML tĩnh)
    _renderMainTable(result);

    // Biểu đồ lực
    _renderForceChart(result);

    // Verdict (pass/fail)
    _renderVerdict(result);
}

/** Render bảng kết quả 4 cột (giống kinematics table M1). */
function _renderMainTable(r) {
    const tbody = document.getElementById("mainResultBody");
    if (!tbody) return;

    const rSec = lbl =>
        `<tr><td colspan="4" style="background:rgba(30,111,255,0.04);padding:8px 14px;
         font-size:9.5px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;
         color:var(--tx3);border-top:1px solid var(--bdr);">${lbl}</td></tr>`;

    const rRow = (label, sym, val, unit, cls = "highlight-cyan") => {
        const disp = typeof val === "number"
            ? (val % 1 === 0 ? val : val.toFixed(3))
            : (val ?? "—");
        return `<tr>
            <td style="text-align:left;">${label}</td>
            <td style="font-family:var(--mono);font-size:11px;color:var(--cyan);text-align:center;">${sym}</td>
            <td class="${cls}">${disp}</td>
            <td style="color:var(--tx3);font-family:var(--mono);font-size:11px;">${unit}</td>
        </tr>`;
    };

    tbody.innerHTML =
        rSec("Loại đai & Thông số tiết diện") +
        rRow("Loại đai chọn",                "—",   r.belt_type,              "—",  "highlight")        +
        rRow("Đường kính bánh nhỏ d₁",       "d₁",  r.d1,                    "mm", "highlight")        +
        rRow("Đường kính bánh lớn d₂",       "d₂",  r.d2,                    "mm", "highlight-teal")   +
        rRow("Vận tốc đai v",                "v",   r.v,                     "m/s", r.v <= 25 ? "highlight-cyan" : "highlight red") +
        rSec("Thông số hình học") +
        rRow("Chiều dài đai tiêu chuẩn L",   "L",   r.L,                    "mm")                       +
        rRow("Khoảng cách trục a",            "a",   r.a,                    "mm")                       +
        rRow("Khoảng điều chỉnh trục a_DC",  "a_DC", r.a_dc ?? "—",         "mm", "")                  +
        rRow("Góc ôm bánh nhỏ α₁",           "α₁",  (r.alpha1 + "°"),       "—",  r.alpha1 >= 120 ? "highlight-teal" : "highlight red") +
        rRow("Tỉ số truyền thực u_tt",       "u_tt", r.u_actual,            "—")                        +
        rRow("Sai số tỉ số truyền Δu",       "Δu",  (r.delta_u + "%"),      "—",  r.delta_u <= 4 ? "highlight-cyan" : "highlight red") +
        rSec("Số đai & Hệ số hiệu chỉnh") +
        rRow("Hệ số góc ôm Cα",              "Cα",  r.Ca,                  "—")                        +
        rRow("Hệ số chiều dài CL",           "CL",  r.Cl,                  "—")                        +
        rRow("Hệ số tỉ số truyền Cu",        "Cu",  r.Cu,                  "—")                        +
        rRow("Hệ số số đai Cz",              "Cz",  r.Cz,                  "—")                        +
        `<tr style="background:rgba(245,158,11,0.04);">
            <td style="text-align:left;font-weight:700;">Số đai chọn Z</td>
            <td style="font-family:var(--mono);font-size:11px;color:var(--cyan);text-align:center;">Z</td>
            <td style="font-family:var(--mono);font-size:20px;font-weight:800;color:var(--gold);">${r.Z}</td>
            <td style="color:var(--tx3);font-family:var(--mono);font-size:11px;">đai</td>
        </tr>` +
        rSec("Kích thước bánh đai") +
        rRow("Chiều rộng bánh đai B",        "B",   r.B,                   "mm", "highlight")          +
        rRow("Đường kính ngoài bánh dẫn da₁","da₁", r.da1,                "mm", "highlight-cyan")     +
        rRow("Đường kính ngoài bánh bị dẫn da₂","da₂", r.da2,            "mm", "highlight-teal")     +
        rSec("Lực trong bộ truyền → M4") +
        rRow("Lực căng ban đầu F₀",          "F₀",  r.F0,                 "N")                        +
        rRow("Lực vòng Ft",                  "Ft",  r.Ft,                 "N")                        +
        `<tr style="background:rgba(245,158,11,0.05);">
            <td style="text-align:left;font-weight:700;">Lực tác dụng lên trục Fr → M4</td>
            <td style="font-family:var(--mono);font-size:11px;color:var(--gold);text-align:center;">Fr</td>
            <td style="font-family:var(--mono);font-size:18px;font-weight:800;color:var(--gold);">${r.Fr}</td>
            <td style="color:var(--tx3);font-family:var(--mono);font-size:11px;">N</td>
        </tr>`;
}

/** Render biểu đồ thanh lực (M1 style). */
function _renderForceChart(r) {
    const el = document.getElementById("chartForce");
    if (!el) return;

    const bars = [
        { label: "Lực ly tâm Fv",          val: r.Fv ?? 0, color: "var(--violet)" },
        { label: "Lực căng ban đầu F₀",    val: r.F0,      color: "var(--teal)"   },
        { label: "Lực vòng Ft",             val: r.Ft,      color: "var(--blue)"   },
        { label: "Lực tác dụng trục Fr",    val: r.Fr,      color: "var(--gold)"   },
    ];

    const max = Math.max(...bars.map(b => b.val), 1);
    el.innerHTML = bars.map(b => {
        const pct = Math.round(b.val / max * 100);
        return `<div class="chart-row">
            <div class="chart-row-label">
                <span>${b.label}</span>
                <span style="font-family:var(--mono);font-size:12px;color:${b.color};">
                    ${b.val.toFixed(1)} N
                </span>
            </div>
            <div class="chart-bar-track">
                <div class="chart-bar-fill"
                     style="width:${pct}%;background:linear-gradient(90deg,${b.color}aa,${b.color});">
                    ${b.val.toFixed(0)} N
                </div>
            </div>
        </div>`;
    }).join("");
}

/** Render verdict pass / fail. */
function _renderVerdict(r) {
    const el = document.getElementById("verdictArea");
    if (!el) return;

    const i_dai = r.v && r.L ? +(r.v * 1000 / r.L).toFixed(3) : 0;
    const allOk =
        r.v <= 25 &&
        r.alpha1 >= 120 &&
        r.delta_u <= 4 &&
        r.Z <= 6 &&
        i_dai <= 10;

    if (allOk) {
        el.innerHTML = `<div class="verdict-box verdict-pass">
            <span style="font-size:24px;">✅</span>
            <div>
                <div class="verdict-title green">BỘ TRUYỀN ĐAI ĐẠT YÊU CẦU</div>
                <div class="verdict-sub">Tất cả điều kiện v, α₁, Δu, Z, i đều thỏa mãn.
                    Xuất Fr = ${r.Fr} N sang Module 4.</div>
            </div>
        </div>`;
    } else {
        const fails = [
            r.v > 25           && `v = ${r.v} m/s > 25`,
            r.alpha1 < 120     && `α₁ = ${r.alpha1}° < 120°`,
            r.delta_u > 4      && `Δu = ${r.delta_u}% > 4%`,
            r.Z > 6            && `Z = ${r.Z} > 6`,
            i_dai > 10         && `i = ${i_dai} > 10`,
        ].filter(Boolean);

        el.innerHTML = `<div class="verdict-box verdict-fail">
            <span style="font-size:24px;">⛔</span>
            <div>
                <div class="verdict-title red">BỘ TRUYỀN CHƯA ĐẠT</div>
                <div class="verdict-sub">Điều chỉnh lại: ${fails.join(" · ")}.</div>
            </div>
        </div>`;
    }
}

/** Cập nhật 5 ô check (step2 table). */
function _renderChecks(r) {
    const i_dai = r.v && r.L ? +(r.v * 1000 / r.L).toFixed(3) : 0;

    setCheck("v",  `${r.v} m/s`,         r.v <= 25);
    setCheck("a1", `${r.alpha1}°`,        r.alpha1 >= 120);
    setCheck("ss", `${r.delta_u}%`,       r.delta_u <= 4);
    setCheck("z",  `${r.Z} đai`,          r.Z <= 6);
    setCheck("i",  `${i_dai} /s`,         i_dai <= 10);
}

/* ══════════════════════════════════════════════════════════════
   5. SAVE MODULE_M2
══════════════════════════════════════════════════════════════ */

/**
 * Lưu toàn bộ kết quả M2 vào localStorage.
 * @param {object} payload – thông số đầu vào đã gửi tính
 * @param {object} result  – kết quả đã chuẩn hoá
 */
function saveM2(payload, result) {
    const { ok, data: m1 } = loadM1();

    const m2Data = {
        input: payload,
        result: {
            belt_type: result.belt_type,
            d1:        result.d1,
            d2:        result.d2,
            v:         result.v,
            L:         result.L,
            a:         result.a,
            alpha1:    result.alpha1,
            Z:         result.Z,
            B:         result.B,
            da1:       result.da1,
            da2:       result.da2,
            F0:        result.F0,
            Ft:        result.Ft,
            Fr:        result.Fr,           // → M4 dùng tiếp
            u_actual:  result.u_actual,
            delta_u:   result.delta_u,
        },
        timestamp: new Date().toISOString(),
    };

    if (ok && m1) {
        m2Data.n2 = m1.kinematics?.truc_1?.n ?? "";
        m2Data.T2 = m1.kinematics?.truc_1?.T ?? "";
        m2Data.u_hop = m1.ratios?.u_1 ?? "";
        m2Data.t_h = m1.input?.lifetime ?? "";
    }

    saveModuleData(STORAGE_KEYS.M2, m2Data);
}

/* ══════════════════════════════════════════════════════════════
   6. goToM3 – chuyển module (gọi từ workflow.js)
══════════════════════════════════════════════════════════════ */

/**
 * Kiểm tra M2 đã lưu và đủ điều kiện trước khi sang M3.
 * Override workflow.js nếu cần kiểm tra thêm.
 */
function goToM3() {
    const m2 = loadModuleData(STORAGE_KEYS.M2);

    if (!m2) {
        showToast("error", "Hãy hoàn thành tính toán bộ truyền đai trước.");
        return;
    }

    const r = m2.result;
    if (!r) {
        showToast("error", "Dữ liệu M2 không hợp lệ — chạy lại tính toán.");
        return;
    }

    // Cảnh báo nhưng vẫn cho sang nếu người dùng biết
    if (r.Z > 6 || r.alpha1 < 120) {
        const ok = window.confirm(
            "⚠️ Bộ truyền đai chưa đạt một số điều kiện kiểm nghiệm.\n" +
            "Bạn vẫn muốn tiếp tục sang Module 3?"
        );
        if (!ok) return;
    }

    saveModuleData(STORAGE_KEYS.PROJECT, {
        currentStep: "M3",
        updatedAt: new Date().toISOString(),
    });

    if (typeof window.navigateTo === "function") {
        window.navigateTo("../m3/UI_banhrangcon.html");
    } else {
        window.location.href = "../m3/UI_banhrangcon.html";
    }
}

/* ══════════════════════════════════════════════════════════════
   7. ENTRY POINT – DOMContentLoaded
══════════════════════════════════════════════════════════════ */

window.addEventListener("DOMContentLoaded", () => {

    // ── 7a. Ngày giờ topbar ──────────────────────────────────────────────
    const tbDate = document.getElementById("tbDate");
    if (tbDate) {
        tbDate.textContent = new Date().toLocaleDateString("vi-VN", {
            weekday: "short", day: "2-digit", month: "2-digit", year: "numeric",
        });
    }

    // ── 7b. Load M1 & prefill ────────────────────────────────────────────
    const { ok, data: m1, error } = loadM1();

    if (!ok) {
        // Hiển thị cảnh báo trên banner nhưng vẫn cho nhập tay
        const banner = document.querySelector(".m1-banner-text");
        if (banner) {
            banner.innerHTML =
                `<span style="color:var(--gold);">⚠️ ${error}</span> — ` +
                `Bạn có thể nhập thủ công bên dưới để kiểm tra.`;
        }
        console.warn("[M2] Không có dữ liệu M1:", error);
    } else {
        prefillFromM1(m1);
    }

    // ── 7c. Restore inputs M2 nếu đã tính trước đó (KHÔNG hiện kết quả tự động) ──
    const m2Saved = loadModuleData(STORAGE_KEYS.M2);
    if (m2Saved?.input) {
        const inp = m2Saved.input;
        setVal("inP1",  inp.power);
        setVal("inN1",  inp.speed);
        setVal("inUd",  inp.ratio);
        setVal("inEps", inp.slip);
        setVal("inKd",  inp.load_factor);
    }

    // ── 7d. Patch nút "Tiếp tục M3" trong HTML để gọi goToM3() ──────────
    document.querySelectorAll("a, button").forEach(el => {
        const txt = el.textContent.toLowerCase();
        if (txt.includes("bánh răng côn") || txt.includes("m3")) {
            el.addEventListener("click", e => {
                e.preventDefault();
                goToM3();
            });
        }
    });
});

/* ══════════════════════════════════════════════════════════════
   8. MAIN RUN – thay thế / bổ sung hàm doRun() trong HTML
      (HTML có thể gọi doRun(); dai.js override nó)
══════════════════════════════════════════════════════════════ */

/**
 * Override hàm doRun() đã khai báo inline trong dai.html.
 * Thứ tự ưu tiên: gọi API backend → nếu lỗi thì dùng tinhDai() nội bộ.
 */
window.doRun = async function doRun() {
    const payload = buildPayload();

    // Validate cơ bản
    if (!payload.power || !payload.speed || !payload.ratio) {
        toast("err", "Vui lòng nhập đầy đủ P₁, n₁ và u_đ!");
        return;
    }

    const btn = document.getElementById("btnRun");
    if (btn) btn.disabled = true;
    const btnIco = document.getElementById("btnIco");
    if (btnIco) btnIco.innerHTML = '<span class="spin">⚙️</span>';

    // Progress bar (nếu có)
    _setProgress(20);

    let result;
    let source = "api";

    try {
        // ── Thử gọi API ─────────────────────────────────────────────────
        result = await callBeltAPI(payload);
        _setProgress(75);
        console.info("[M2] Kết quả từ API backend:", result);

    } catch (apiErr) {
        console.warn("[M2] API không khả dụng, dùng tính toán nội bộ:", apiErr.message);
        toast("warn", `Backend offline — đang dùng tính toán nội bộ`);

        try {
            result = runLocal(payload);
            _setProgress(75);
            source = "local";
        } catch (localErr) {
            toast("err", localErr.message);
            _resetBtn();
            _setProgress(0);
            return;
        }
    }

    // ── Hiện Step 2: bảng kiểm nghiệm ───────────────────────────────────
    _showStep("step2");
    await _wait(100);
    _renderChecks(result);

    // ── Hiện Step 3: kết quả tổng hợp ───────────────────────────────────
    _showStep("step3");
    renderResult(result);

    // ── Lưu M2 vào localStorage ──────────────────────────────────────────
    saveM2(payload, result);
    _setProgress(100);

    // ── Toast tóm tắt ────────────────────────────────────────────────────
    const src = source === "api" ? "API" : "Nội bộ";
    toast("ok",
        `[${src}] Đai ${result.belt_type} · d₁=${result.d1}/d₂=${result.d2} mm · ` +
        `Z=${result.Z} · Fr=${result.Fr} N — Đã lưu M2`);

    _resetBtn();
};

/* ══════════════════════════════════════════════════════════════
   9. RESTORE KHI RELOAD
══════════════════════════════════════════════════════════════ */

/**
 * Khôi phục giao diện từ dữ liệu M2 đã lưu (khi user reload trang).
 * @param {object} m2Saved – object từ loadModuleData(STORAGE_KEYS.M2)
 */
function _restoreM2(m2Saved) {
    if (!m2Saved?.result) return;

    const r = m2Saved.result;
    const inp = m2Saved.input;

    // Restore inputs
    if (inp) {
        setVal("inP1",  inp.power);
        setVal("inN1",  inp.speed);
        setVal("inUd",  inp.ratio);
        setVal("inEps", inp.slip);
        setVal("inKd",  inp.load_factor);
    }

    // Hiện step 2 & 3
    _showStep("step2");
    _showStep("step3");

    // Render kết quả
    _renderChecks(r);
    renderResult(r);

    console.info("[M2] Đã restore từ localStorage.");
}

/* ══════════════════════════════════════════════════════════════
   10. PRIVATE HELPERS
══════════════════════════════════════════════════════════════ */

/** Gán giá trị an toàn cho input (bỏ qua nếu element không tồn tại). */
function setVal(id, val) {
    const el = document.getElementById(id);
    if (!el || val === undefined || val === null) return;
    el.value = val;
}

function _showStep(id) {
    const el = document.getElementById(id);
    if (el) el.classList.add("active");
}

function _setProgress(p) {
    const fill = document.getElementById("progFill");
    const pct  = document.getElementById("progPct");
    if (fill) fill.style.width = p + "%";
    if (pct)  pct.textContent  = p + "%";
}

function _resetBtn() {
    const btn    = document.getElementById("btnRun");
    const btnIco = document.getElementById("btnIco");
    if (btn)    btn.disabled        = false;
    if (btnIco) btnIco.textContent  = "⚙️";
}

function _wait(ms) {
    return new Promise(r => setTimeout(r, ms));
}

/**
 * setCheck và toast đã được định nghĩa inline trong dai.html.
 * Khai báo lại ở đây phòng trường hợp dai.js được dùng độc lập.
 */
if (typeof setCheck !== "function") {
    window.setCheck = function(id, val, pass, idle) {
        const ckEl  = document.getElementById("ck-"  + id);
        const cksEl = document.getElementById("cks-" + id);
        if (ckEl)  ckEl.textContent = val;
        if (!cksEl) return;
        if (idle) { cksEl.className = "chk-tag idle"; cksEl.textContent = "—"; return; }
        cksEl.className  = "chk-tag " + (pass ? "pass" : "fail");
        cksEl.textContent = pass ? "PASS ✓" : "FAIL ✗";
    };
}

if (typeof toast !== "function") {
    window.toast = function(type, msg) {
        const w = document.getElementById("toastWrap");
        if (!w) return console.log(`[Toast ${type}] ${msg}`);
        const t = document.createElement("div");
        const ic = { ok: "✅", err: "❌", warn: "⚠️" };
        t.className = `toast t-${type}`;
        t.innerHTML = `<span class="toast-ico">${ic[type] || "ℹ️"}</span>` +
                      `<span class="toast-msg">${msg}</span>` +
                      `<span class="toast-x" onclick="this.parentElement.remove()">✕</span>`;
        w.appendChild(t);
        setTimeout(() => {
            t.style.cssText += "opacity:0;transform:translateX(16px);transition:all 0.28s;";
            setTimeout(() => t.remove(), 300);
        }, 5500);
    };
}

if (typeof showToast !== "function") {
    window.showToast = (type, msg) => toast(type === "error" ? "err" : type, msg);
}
