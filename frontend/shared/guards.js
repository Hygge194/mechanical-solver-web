function requireModule(moduleKey, redirectTo) {

    const data = loadModuleData(moduleKey);

    if(!data) {

        alert(
            `Thiếu dữ liệu ${moduleKey}`
        );

        window.location.href = redirectTo;

        return false;
    }

    return true;
}