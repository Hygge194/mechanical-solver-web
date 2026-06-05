const WORKFLOW = {

    MODULES: {

        M1: "../m1/m1_input_validation.html",

        M2: "../m2/dai.html",

        M3: "../m3/UI_banhrangcon.html",

        M4: "../m4/UI_banhrangtru.html"
    }
};

// ── Hàm điều hướng chung tự nhận diện thư mục gốc/con ──────────────────
window.navigateTo = function(pathFromSub) {
    const isRoot = !window.location.pathname.includes("/m1/") &&
                   !window.location.pathname.includes("/m2/") &&
                   !window.location.pathname.includes("/m3/") &&
                   !window.location.pathname.includes("/m4/");
    let target = pathFromSub;
    if (isRoot) {
        target = pathFromSub.replace(/^\.\.\//, "");
    }
    window.location.href = target;
};

function goToM1() {
    saveModuleData(STORAGE_KEYS.PROJECT, {
        currentStep: "M1",
        updatedAt: new Date().toISOString()
    });

    window.navigateTo("../m1/m1_input_validation.html");
}

/**
 * Chuyển sang Module M2 – Bộ truyền đai
 * Kiểm tra dữ liệu M1 hợp lệ trước khi chuyển trang
 */
function goToM2() {
    const m1 = loadModuleData(STORAGE_KEYS.M1);

    if (!m1) {
        showToast("error", "Hãy hoàn thành Module 1 trước khi tiếp tục.");
        return;
    }

    if (!m1.validation || !m1.validation.is_valid) {
        showToast("error", "Động cơ chưa đạt kiểm nghiệm khởi động quá tải. Vui lòng điều chỉnh hệ số K_qt.");
        return;
    }

    // Đánh dấu trạng thái workflow
    saveModuleData(STORAGE_KEYS.PROJECT, {
        currentStep: "M2",
        updatedAt: new Date().toISOString()
    });

    // Chuyển trang sang M2
    window.navigateTo("../m2/dai.html");
}

/**
 * Chuyển sang Module M3 – Bánh răng côn
 */
function goToM3() {
    const m2 = loadModuleData(STORAGE_KEYS.M2);

    if (!m2) {
        showToast("error", "Hãy hoàn thành Module 2 trước khi tiếp tục.");
        return;
    }

    saveModuleData(STORAGE_KEYS.PROJECT, {
        currentStep: "M3",
        updatedAt: new Date().toISOString()
    });

    window.navigateTo("../m3/UI_banhrangcon.html");
}

/**
 * Chuyển sang Module M4 – Bánh răng trụ
 */
function goToM4() {
    const m3 = loadModuleData(STORAGE_KEYS.M3);

    if (!m3) {
        showToast("error", "Hãy hoàn thành Module 3 trước khi tiếp tục.");
        return;
    }

    saveModuleData(STORAGE_KEYS.PROJECT, {
        currentStep: "M4",
        updatedAt: new Date().toISOString()
    });

    window.navigateTo("../m4/UI_banhrangtru.html");
}

// ── Fallback showToast để tránh ReferenceError ───────────────────
if (typeof showToast !== "function") {
    window.showToast = function(type, msg) {
        if (typeof toast === "function") {
            toast(type === "error" ? "err" : type, msg);
        } else {
            console.warn(`[Toast] [${type}] ${msg}`);
        }
    };
}

// ── Tự động gắn sự kiện chuyển trang cho sidebar và pipeline ────
document.addEventListener("DOMContentLoaded", () => {

    // Patch all sidebar nav links
    document.querySelectorAll(".nav-link").forEach(el => {
        const text = el.textContent.toLowerCase();
        if (text.includes("động cơ") || text.includes("m1")) {
            el.addEventListener("click", (e) => {
                e.preventDefault();
                if (typeof goToM1 === "function") goToM1();
                else window.navigateTo("../m1/m1_input_validation.html");
            });
        } else if (text.includes("đai") || text.includes("m2")) {
            el.addEventListener("click", (e) => {
                e.preventDefault();
                if (typeof goToM2 === "function") goToM2();
                else window.navigateTo("../m2/dai.html");
            });
        } else if (text.includes("côn") || text.includes("m3")) {
            el.addEventListener("click", (e) => {
                e.preventDefault();
                if (typeof goToM3 === "function") goToM3();
                else window.navigateTo("../m3/UI_banhrangcon.html");
            });
        } else if (text.includes("trụ") || text.includes("m4")) {
            el.addEventListener("click", (e) => {
                e.preventDefault();
                if (typeof goToM4 === "function") goToM4();
                else window.navigateTo("../m4/UI_banhrangtru.html");
            });
        }
    });

    // Patch progress pipeline steps
    document.querySelectorAll(".pipe-step, .pipe-dot").forEach(el => {
        const text = el.textContent.trim().toUpperCase();
        if (text === "M1") {
            el.addEventListener("click", (e) => {
                e.preventDefault();
                if (typeof goToM1 === "function") goToM1();
                else window.navigateTo("../m1/m1_input_validation.html");
            });
        } else if (text === "M2") {
            el.addEventListener("click", (e) => {
                e.preventDefault();
                if (typeof goToM2 === "function") goToM2();
                else window.navigateTo("../m2/dai.html");
            });
        } else if (text === "M3") {
            el.addEventListener("click", (e) => {
                e.preventDefault();
                if (typeof goToM3 === "function") goToM3();
                else window.navigateTo("../m3/UI_banhrangcon.html");
            });
        } else if (text === "M4") {
            el.addEventListener("click", (e) => {
                e.preventDefault();
                if (typeof goToM4 === "function") goToM4();
                else window.navigateTo("../m4/UI_banhrangtru.html");
            });
        }
    });
});