from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import (
    db,
    Field,
    session,
    T,
    cache,
    auth,
    logger,
    authenticated,
    unauthenticated,
    flash,
)
from py4web.utils.form import Form, FormStyleBulma
from pydal.validators import *
from .models import MTROUTE_TYPES, MOROUTE_TYPES
from .common import jasmin
from .utils import cols_split


@action("imt_remove/<order>", method=["GET", "POST"])
def imt_remove(order):
    script = ""
    filters = ""
    order = order
    resp = jasmin.interceptor(["mt", "remove", order, script, filters[:-1]])
    if resp:
        flash.set(resp)
    else:
        flash.set("Removed MO Interceptor with order %s" % order)
        query = (db.j_imt.mtorder == order) & (db.j_imt.gw == session.g_id)
        db(query).delete()
    redirect(URL("manage_imt"))


def get_imts():
    imts = []
    rows = jasmin.list_it("imts")
    if not rows:
        return imts

    else:
        lines = rows
        tt = cols_split(lines[2:-2])
        imt = {}
        for t in tt:
            imt = {"i_order": "", "i_type": "", "i_script": "", "i_filter": ""}
            n = len(t)
            imt.update(i_order=t[0][1:], i_type=t[1], i_script=t[2])
            i = 3
            if t[1] == "StaticMTInterceptor":
                while t[i][0] != "<":
                    test = t[i][0]
                    imt.update(i_script=imt["i_script"] + " " + t[i])
                    i += 1
                while i < n:
                    imt.update(i_filter=imt["i_filter"] + " " + t[i])
                    i += 1
                imts.append(imt)
            else:
                while i < n:
                    imt.update(i_script=imt["i_script"] + " " + t[i])
                    i += 1
                imts.append(imt)
    return imts


@action("manage_imts", method=["GET", "POST"])
@action.uses(db, session, auth, flash, "list_interceptors.html")
def manage_imts():
    title = "Manage MT Interceptors"
    form = Form(db.j_imt, formstyle=FormStyleBulma)
    # print(f"form: {form}")
    if form.accepted:
        order = form.vars.get("mtorder")
        i_type = form.vars.get("mttype")
        script = "python3(" + form.vars.get("mtscript") + ")"
        if i_type != "DefaultInterceptor":
            ff = ""
            for f in form.vars.get("mtfilters"):
                ff += db.mt_filter[f].fid
                # get_f_name(f)
                ff += ";"
            filters = ff
        else:
            filters = ""
            order = "0"
            form.vars["mtorder"] = "0"
            form.vars["mtfilters"] = ""

        resp = jasmin.interceptor(["mt", i_type, order, script, filters[:-1]])
        if not resp:
            id = db.j_imt.insert(**db.j_imt._filter_fields(form.vars))
            flash.set("Added a %s with order %s" % (form.vars.get("mttype"), order))
        else:
            flash.set(resp)
    imts = get_imts()
    print(f"imts: {imts}")
    return dict(form=form, imts=imts, type="mt", title=title)


@action("imo_remove/<order>", method=["GET", "POST"])
def imo_remove(order):
    script = ""
    filters = ""
    order = order
    resp = jasmin.interceptor(["mo", "remove", order, script, filters[:-1]])
    if not resp:
        session.set("Removed MO Interceptor with order %s" % order)
        query = (db.j_imo.moorder == order) & (db.j_imo.gw == session.g_id)
        db(query).delete()
    else:
        flash.set(resp)
    redirect(URL("manage_imos"))


def get_imos():
    imos = []
    rows = jasmin.list_it("imos")
    if not rows:
        return imos

    else:
        lines = rows
        # print(f"lines: {lines}")
        tt = cols_split(lines[2:-2])
        # print(f"tt: {tt}")
        imo = {}
        for t in tt:
            n = len(t)
            imo = {"i_order": "", "i_type": "", "i_script": "", "i_filter": ""}
            imo.update(i_order=t[0][1:], i_type=t[1], i_script=t[2])
            i = 3
            if t[1] == "StaticMOInterceptor":
                while t[i][0] != "<":
                    test = t[i][0]
                    imo.update(i_script=imo["i_script"] + " " + t[i])
                    i += 1
                while i < n:
                    imo.update(i_filter=imo["i_filter"] + " " + t[i])
                    i += 1
                imos.append(imo)
            else:
                while i < n:
                    imo.update(i_script=imo["i_script"] + " " + t[i])
                    i += 1
                imos.append(imo)
    return imos


@action("manage_imos", method=["GET", "POST"])
@action.uses(db, session, auth, flash, "list_interceptors.html")
def manage_imos():
    title = "Manage MO Interceptors"
    form = Form(db.j_imo, formstyle=FormStyleBulma)
    if form.accepted:
        # print(f"form vars: {form.vars}")
        order = form.vars.get("moorder")
        # print(f"order: {order}")
        i_type = form.vars.get("motype")
        # print(f"type: {i_type}")
        script = "python3(" + form.vars.get("moscript") + ")"
        if i_type != "DefaultInterceptor":
            ff = ""
            for f in form.vars.get("mofilters"):
                ff += db.mt_filter[f].fid
                # get_f_name(f)
                ff += ";"
            filters = ff
        else:
            filters = ""
            order = "0"
            form.vars.moorder = "0"
            form.vars.mofilters = ""
        resp = jasmin.interceptor(["mo", i_type, order, script, filters[:-1]])
        if not resp:
            id = db.j_imo.insert(**db.j_imo._filter_fields(form.vars))
            flash.set("Added a MO %s with order %s" % (form.vars.get("motype"), order))
        else:
            flash.set(resp)
    imos = get_imos()
    print(f"imos: {imos}")
    return dict(form=form, imts=imos, type="mo", title=title)
