from flask import render_template, request, redirect, url_for
from flask_login import login_required

from .. import bp
from ..forms import EditProfileAdminForm
from ...decorators import admin_required
from ...lang import WORDINGS
from ...models import db, User, Role
from ...utils import display_success_toast


@bp.route("/edit-profile/<int:user_id>", methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(user_id):
    title = "Modification de profil"
    user = User.query.get_or_404(user_id)
    form = EditProfileAdminForm(user=user)

    if request.method == "GET":
        form.email.data = user.email
        form.username.data = user.username
        form.confirmed.data = user.confirmed
        form.role.data = user.role
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        db.session.add(user)
        display_success_toast(WORDINGS.AUTH.PROFILE_UPDATED)
        return redirect(
            url_for(
                ".view_user",
                user_id=user.id
            )
        )

    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id

    return render_template(
        "main/edit_profile.html",
        form=form,
        user=user,
        title=title
    ) 

