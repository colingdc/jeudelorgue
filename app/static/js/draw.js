function fill_next_round(match_position, player_position) {
    // find id of origin div : id = player-{{match_position}}-{{player_position}}
    origin_id = "#player-" + match_position + "-" + player_position;

    // find id of destination div
    next_match_position = Math.floor(match_position / 2);
    next_player_position = match_position % 2;
    destination_id = "#player-" + next_match_position + "-" + next_player_position;

    // fiil text of destination with text of origin
    $(destination_id).text($(origin_id).text());

    // fill tournament_player_id attribute with origin tournament_player_id
    $(destination_id).attr("tournament_player_id", $(origin_id).attr("tournament_player_id"));
    update_json();
}

function update_json() {
    var res = {};
    $(".match").each(function() {
        match_position = $(this).attr("match_position_id");
        next_match_position = Math.floor(match_position / 2);
        next_player_position = match_position % 2;
        destination_id = "#player-" + next_match_position + "-" + next_player_position;

        res[$(this).attr("match_id")] = $(destination_id).attr("tournament_player_id");
    })
    $("#forecast").attr("value", JSON.stringify(res));

}
