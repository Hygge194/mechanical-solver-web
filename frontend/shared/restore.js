function restoreInput(id, value) {

    const el =
        document.getElementById(id);

    if(!el) return;

    el.value = value;
}