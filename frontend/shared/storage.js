const STORAGE_KEYS = {
    M1: "MODULE_M1",
    M2: "MODULE_M2",
    M3: "MODULE_M3",
    M4: "MODULE_M4",
    PROJECT: "PROJECT_DATA"
};

function saveModuleData(key, data) {

    localStorage.setItem(
        key,
        JSON.stringify(data)
    );

    updateProjectData(key, data);
}

function loadModuleData(key) {

    const data = localStorage.getItem(key);

    if (!data) return null;

    return JSON.parse(data);
}

function updateProjectData(moduleKey, moduleData) {

    let project =
        JSON.parse(localStorage.getItem(STORAGE_KEYS.PROJECT))
        || {};

    project[moduleKey] = moduleData;

    localStorage.setItem(
        STORAGE_KEYS.PROJECT,
        JSON.stringify(project)
    );
}

function loadProjectData() {

    return JSON.parse(
        localStorage.getItem(STORAGE_KEYS.PROJECT)
    ) || {};
}

function clearProjectData() {

    localStorage.clear();
}