(this["webpackJsonpstreamlit-agraph"] = this["webpackJsonpstreamlit-agraph"] || []).push([
    [0], {
        54: function(n, t, e) {
            n.exports = e(71)
        },
        71: function(n, t, e) {
            "use strict";
            e.r(t);
            var c = e(5),
                a = e.n(c),
                o = e(48),
                i = e.n(o),
                r = e(0),
                l = e(1),
                d = e(2),
                u = e(34),
                s = e(50),
                p = function(n) {
                    Object(l.a)(e, n);
                    var t = Object(d.a)(e);

                    function e() {
                        var n;
                        Object(r.a)(this, e);
                        for (var c = arguments.length, o = new Array(c), i = 0; i < c; i++) o[i] = arguments[i];
                        return (n = t.call.apply(t, [this].concat(o))).state = {
                            numClicks: 0
                        }, n.render = function() {
                            var t = JSON.parse(n.props.args.data),
                                e = JSON.parse(n.props.args.config);
                            return a.a.createElement(s.Graph, {
                                id: "graph-id",
                                data: t,
                                config: e,
                                onClickNode: function(n) {
                                    const arr = n.split('_');
                                    if (arr[0] === 'NOTE'){
                                        window.open('bear://x-callback-url/open-note?id='.concat(arr[1]), '_self');
                                    }else if (arr[0] === 'TAG'){
                                        window.open('bear://x-callback-url/open-tag?name='.concat(arr[1].replaceAll('/', '%2F')), '_self');

                                    }
                                },
                                onDoubleClickNode: function(n) {
                                    // window.alert("Double clicked node ".concat(n))
                                },
                                onRightClickNode: function(n, t) {
                                    // window.alert("Right clicked node ".concat(t))
                                },
                                onClickLink: function(n, t) {
                                    // window.alert("Clicked link between ".concat(n.split('_')[1], " and ").concat(t.split('_')[1]))
                                },
                                onRightClickLink: function(n, t, e) {
                                    // window.alert("Right clicked link between ".concat(t.split('_')[1], " and ").concat(e.split('_')[1]))
                                }
                            })
                        }, n
                    }
                    return e
                }(u.a),
                k = Object(u.b)(p);
            i.a.render(a.a.createElement(a.a.StrictMode, null, a.a.createElement(k, null)), document.getElementById("root"))
        }
    },
    [
        [54, 1, 2]
    ]
]);
//# sourceMappingURL=main.081b8332.chunk.js.map