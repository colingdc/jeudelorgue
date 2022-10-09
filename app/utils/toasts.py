from flask import flash


def display_error_toast(message):
    flash(message, "error")


def display_info_toast(message):
    flash(message, "info")


def display_success_toast(message):
    flash(message, "success")


def display_warning_toast(message):
    flash(message, "warning")
