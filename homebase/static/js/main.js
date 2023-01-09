var hitters_field = document.getElementById('hitters')
var pitchers_field = document.getElementById('pitchers')
var hitters_table = document.getElementById('hitters_tbl')
var pitchers_table = document.getElementById('pitchers_tbl')

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
