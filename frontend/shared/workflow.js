const WORKFLOW = {

    MODULES: {

        M1: "../m1/m1.html",

        M2: "../m2/dai.html",

        M3: "../m3/banhrangcon.html",

        M4: "../m4/banhrangtru.html"
    }
};

/**
 * MechaMix – shared/workflow.js
 * Điều hướng giữa các Module và quản lý trạng thái workflow
 */

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
    window.location.href = "../m2/dai.html";
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

    window.location.href = "../m3/banhrangcon.html";
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

    window.location.href = "../m4/banhrangtru.html";
}