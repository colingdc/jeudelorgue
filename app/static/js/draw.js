function fill_next_round(event, match_position, player_position) {
    // find id of origin div : id = player-{{match_position}}-{{player_position}}
    origin_id = "#player-" + match_position + "-" + player_position;


    if (event.ctrlKey || event.metaKey) {
        // fiil text of destination with text of origin
        $(origin_id).text("\xa0");

        // fill tournament_player_id attribute with origin tournament_player_id
        $(origin_id).attr("tournament_player_id", "None");
    }

    else {
        // find id of destination div
        next_match_position = Math.floor(match_position / 2);
        next_player_position = match_position % 2;
        destination_id = "#player-" + next_match_position + "-" + next_player_position;

        // fill text of destination with text of origin
        $(destination_id).text($(origin_id).text());

        // fill tournament_player_id attribute with origin tournament_player_id
        $(destination_id).attr("tournament_player_id", $(origin_id).attr("tournament_player_id"));

        // find other player id
        if (player_position == "0") {
            other_player_id = "#player-" + match_position + "-1";
        } else {
            other_player_id = "#player-" + match_position + "-0";
        }

        // Get corresponding tournament player id
        other_tournament_player_id = $(other_player_id).attr("tournament_player_id")
        $(".game-player").each(function() {
            if ($(this).attr("tournament_player_id") == other_tournament_player_id
                & $(this).attr("match_position_id") < match_position) {
                $(this).attr("tournament_player_id", "None");
                $(this).text("\xa0");
                console.log($(this).attr("match_position_id"))
            }
        })
    }

    update_json();
}

match_position=3
player_position=0
origin_id = "#player-" + match_position + "-" + player_position;
other_player_id = "#player-" + match_position + "-1"
other_tournament_player_id = $(other_player_id).attr("tournament_player_id")

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

function show_real_winners() {
    $(".to_hide").each(function() {
        $(this).hide()
        })
    $(".to_show").each(function() {
        $(this).show()
        })
}

function hide_real_winners() {
    $(".to_show").each(function() {
        $(this).hide()
        })
    $(".to_hide").each(function() {
        $(this).show()
        })
}
