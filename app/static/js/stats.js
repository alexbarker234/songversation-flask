$(document).ready(function () {
    $(".sortable").on("click", function () {
        var $table = $(this).closest("table");
        var columnIndex = $(this).index();
        var rows = $table.find("tbody tr").get();
        var isAscending = $(this).data("sort") === "asc";

        rows.sort(function (a, b) {
            var aValue = $(a).find("td").eq(columnIndex).text().trim();
            var bValue = $(b).find("td").eq(columnIndex).text().trim();

            if (isAscending) {
                return aValue.localeCompare(bValue, undefined, { numeric: true });
            } else {
                return bValue.localeCompare(aValue, undefined, { numeric: true });
            }
        });

        $table.find("tbody").empty().append(rows);
        $(this).data("sort", isAscending ? "desc" : "asc");

        $(".sortable .fa").hide();
        var $sortIcon = $(this).find(".fa");
        $sortIcon.show();
        $sortIcon.removeClass("fa-caret-up fa-caret-down").addClass(isAscending ? "fa-caret-up" : "fa-caret-down");
    });

    $('.tracklist-selector').on('click', function(e) {
        target = $(e.target)
        if (target.hasClass('disabled')) return;

        id = target.attr('id')
        type = id.split('-')[0]
        chooseStatsTable(type)

    }) 
});

function chooseStatsTable(type) {
    if (type == 'playlist') {
        $('#artist-table').css('display', 'none')
        $('#playlist-table').removeAttr('style')
    }
    else {
        $('#playlist-table').css('display', 'none')
        $('#artist-table').removeAttr('style')
    }
}