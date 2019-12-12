import bottle
from model import Film


@bottle.get('/najboljsi/<leto:int>/')
def najboljsi_filmi(leto):
    return bottle.template(
        'najboljsi_filmi.html',
        leto=leto,
        filmi=Film.najboljsi_v_letu(leto)
    )


bottle.run(debug=True, reloader=True)
