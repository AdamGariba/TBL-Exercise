var hitters_field = document.getElementById('hitters')
var pitchers_field = document.getElementById('pitchers')
var hitters_table = document.getElementById('hitters_tbl')
var pitchers_table = document.getElementById('pitchers_tbl')

// Set the Hitters table to be shown on default
window.onload = (event) => {
    hitters_field.checked = true;
    hitters_table.style.display = "table";
    pitchers_table.style.display = "none";
};

// Toggles between the hitters and pitchers table
function showTable() {
    if(hitters_field.checked) {
        hitters_table.style.display = "table";
        pitchers_table.style.display = "none";
    }
    else if(pitchers_field.checked) {
        pitchers_table.style.display = "table";
        hitters_table.style.display = "none";
    }
}
