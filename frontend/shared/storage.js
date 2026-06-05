const STORAGE_KEYS = {
    M1: "M1_Data",
    M2: "M2_Data",
    M3: "M3_Data",
    M4: "M4_Data",
    PROJECT: "PROJECT_DATA"
};

function saveModuleData(key, data) {

    localStorage.setItem(
        key,
        JSON.stringify(data)
    );

    updateProjectData(key, data);
}

function saveData(key, data) {
    saveModuleData(key, data);
}

function loadData(key) {
    return loadModuleData(key);
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