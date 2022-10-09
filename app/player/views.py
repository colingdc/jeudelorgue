# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, url_for, current_app
import datetime

from . import bp
from .forms import CreatePlayerForm, EditPlayerForm
from .. import db
from ..decorators import manager_required
from ..models import Player
from ..lang import WORDINGS
from ..utils import display_info_toast


@bp.route("/create", methods=["GET", "POST"])
@manager_required
def create_player():
    form = CreatePlayerForm(request.form)
    if form.validate_on_submit():
        player = Player(
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        db.session.add(player)
        db.session.commit()
        display_info_toast(WORDINGS.PLAYER.PLAYER_CREATED.format(player.get_full_name()))
        return redirect(url_for(".create_player"))
    else:
        return render_template(
            "player/create_player.html",
            title=WORDINGS.PLAYER.CREATE_PLAYER,
            form=form
        )


@bp.route("/<player_id>/edit", methods=["GET", "POST"])
@manager_required
def edit_player(player_id):
    player = Player.query.get_or_404(player_id)
    title = player.get_full_name()
    form = EditPlayerForm(request.form)
    if request.method == "GET":
        form.first_name.data = player.first_name
        form.last_name.data = player.last_name
    if form.validate_on_submit():
        player.first_name = form.first_name.data
        player.last_name = form.last_name.data
        db.session.add(player)
        db.session.commit()
        display_info_toast(WORDINGS.PLAYER.PLAYER_UPDATED.format(player.get_full_name()))
        return redirect(
            url_for(
                ".edit_player",
                player_id=player_id
            )
        )
    else:
        return render_template(
            "player/edit_player.html",
            title=title,
            form=form,
            player=player
        )


@bp.route("/<player_id>/delete")
@manager_required
def delete_player(player_id):
    player = Player.query.get_or_404(player_id)
    player.deleted_at = datetime.datetime.now()
    db.session.add(player)
    db.session.commit()
    display_info_toast(WORDINGS.PLAYER.PLAYER_DELETED.format(player.get_full_name()))
    return redirect(url_for(".view_players"))


@bp.route("/<player_id>")
@manager_required
def view_player(player_id):
    player = Player.query.get_or_404(player_id)
    title = player.get_full_name()
    return render_template(
        "player/view_player.html",
        title=title,
        player=player
    )


@bp.route("/all")
@manager_required
def view_players():
    page = request.args.get("page", 1, type=int)
    pagination = (Player.query.order_by(Player.last_name, Player.first_name)
                  .filter(Player.deleted_at.is_(None))
                  .paginate(page, per_page=current_app.config["PLAYERS_PER_PAGE"], error_out=False))

    return render_template(
        "player/view_players.html",
        title=WORDINGS.PLAYER.PLAYERS,
        pagination=pagination
    )
