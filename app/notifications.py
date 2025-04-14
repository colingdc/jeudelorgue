from flask import flash


def display_success_message(message):
    flash(message, "success")


def display_info_message(message):
    flash(message, "info")


def display_warning_message(message):
    flash(message, "warning")


def display_error_message(message):
    flash(message, "error")
