
    const TOKEN = document.getElementById("ui_token").innerText;

    const MESSAGE_TYPES = {
        CONN_BASE: "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/connections/1.0/",
        UI_BASE: "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/sovrin.org/ui/1.0/"};

    const UI_MESSAGE = {
        STATE: MESSAGE_TYPES.UI_BASE + "state",
        STATE_REQUEST: MESSAGE_TYPES.UI_BASE + "state_request",
        INITIALIZE: MESSAGE_TYPES.UI_BASE + "initialize",

        SEND_INVITE: MESSAGE_TYPES.UI_BASE + "send_invite",
        INVITE_SENT: MESSAGE_TYPES.UI_BASE + "invite_sent",
        INVITE_RECEIVED: MESSAGE_TYPES.UI_BASE + "invite_received",

        SEND_REQUEST: MESSAGE_TYPES.UI_BASE + "send_request",
        REQUEST_SENT: MESSAGE_TYPES.UI_BASE + "request_sent",

        SEND_RESPONSE: MESSAGE_TYPES.UI_BASE + "send_response",
        RESPONSE_SENT: MESSAGE_TYPES.UI_BASE + "response_sent",
    };

    const CONN_MESSAGE = {
        REQUEST_RECEIVED:MESSAGE_TYPES.CONN_BASE + "request",
        RESPONSE_RECEIVED: MESSAGE_TYPES.CONN_BASE + "response"
    };

    // Message Router {{{
    var msg_router = {
        routes: [],
        route:
            function(msg) {
                if (msg.type in this.routes) {
                    this.routes[msg.type](msg);
                } else {
                    console.log('Message from server without registered route: ' + JSON.stringify(msg));
                }
            },
        register:
            function(msg_type, fn) {
                this.routes[msg_type] = fn
            }
    };
    // }}}

    // this is shared data among all the vue instances for simplicity.
    var ui_data = {
        agent_name: '',
        passphrase: '',
        current_tab: 'login',
        new_connection_offer: {
            name: "",
            endpoint: ""
        },
        connections: [],
        history_view: []
    };

    var ui_credentials = new Vue({
        el: '#credentials',
        data: ui_data,
        computed: {
            tab_active: function(){
                return this.current_tab == "credentials";
            }
        }
    });

    var ui_relationships = new Vue({
        el: '#relationships',
        data: ui_data,
        computed: {
            tab_active: function(){
                return this.current_tab == "relationships";
            }
        },
        methods: {
            send_invite: function () {
                msg = {
                    type: UI_MESSAGE.SEND_INVITE,
                    id: TOKEN,
                    content: {
                        name: this.new_connection_offer.name,
                        endpoint: this.new_connection_offer.endpoint
                    }
                };
                socket.send(JSON.stringify(msg));
            },
            invite_sent: function (msg) {
                this.connections.push({
                    name: msg.content.name,
                    status: "Invite Sent",
                    history: []
                });
            },
            invite_received: function (msg) {
                this.connections.push({
                    name: msg.content.name,
                    invitation_msg: msg.content,
                    status: "Invite Received",
                    history: [history_format(msg.content.history)]
                });
            },

            send_request: function (invitation_msg) {
                msg = {
                    type: UI_MESSAGE.SEND_REQUEST,
                    id: TOKEN,
                    content: {
                            name: invitation_msg.name,
                            endpoint: invitation_msg.endpoint.url,
                            key: invitation_msg.endpoint.verkey,
                    }
                };
                socket.send(JSON.stringify(msg));
            },
            request_sent: function (msg) {
                var c = this.connections.find(function(x){return x.name === msg.content.name;});
                c.status = "Request Sent";
            },
            request_received: function (msg) {

                var c = this.connections.find(function(x){return x.name === msg.content.name;});
                c.status = "Request Received";
                c.connecton_request = msg.content;
                c.history.push(history_format(msg.content.history));

            },
            send_response: function (prevMsg) {
                msg = {
                    type: UI_MESSAGE.SEND_RESPONSE,
                    id: TOKEN,
                    content: {
                            name: prevMsg.name,
                            endpoint_key: prevMsg.endpoint_key,
                            endpoint_uri: prevMsg.endpoint_uri,
                            endpoint_did: prevMsg.endpoint_did
                    }
                };
                socket.send(JSON.stringify(msg));
            },
            response_sent: function (msg) {
                var c = this.connections.find(function(x){return x.name === msg.content.name;});
                c.status = "Response sent";
                c.history.push(history_format(msg.content));

            },
            response_received: function (msg) {
                var c = this.connections.find(function(x){return x.name === msg.content.name;});
                c.status = "Response received";
                c.history.push(history_format(msg.content.history));
            },
            display_history: function(connection){
                this.history_view = connection.history;
                console.log(this.history_view);
                $('#historyModal').modal({});
            }
        }
    });

    // UI Agent {{{
    var ui_agent = new Vue({
        el: '#login',
        data: ui_data,
        computed: {
            tab_active: function(){
                return this.current_tab == "login";
            }
        },
        methods: {
            initialize: function () {
                init_message = {
                    type: UI_MESSAGE.INITIALIZE,
                    id: TOKEN,
                    content: {
                        name: this.agent_name,
                        passphrase: this.passphrase
                    }
                };
                socket.send(JSON.stringify(init_message));
            },
            connect: function(){
                socket.send(JSON.stringify(
                    {
                        type: UI_MESSAGE.STATE_REQUEST,
                        id: TOKEN,
                        content: null
                    }
                ));
            },
            update: function (msg) {
                state = msg.content;
                if (state.initialized === false) {
                    this.current_tab = 'login';
                } else {
                    this.agent_name = state.agent_name;
                    this.current_tab = 'relationships';
                }
            }
        }
    });


    // }}}

    // Message Routes {{{
    msg_router.register(UI_MESSAGE.STATE, ui_agent.update);
    msg_router.register(UI_MESSAGE.INVITE_SENT, ui_relationships.invite_sent);
    msg_router.register(UI_MESSAGE.INVITE_RECEIVED, ui_relationships.invite_received);
    msg_router.register(UI_MESSAGE.REQUEST_SENT, ui_relationships.request_sent);
    msg_router.register(CONN_MESSAGE.RESPONSE_RECEIVED, ui_relationships.response_received);
    msg_router.register(CONN_MESSAGE.REQUEST_RECEIVED, ui_relationships.request_received);
    msg_router.register(UI_MESSAGE.RESPONSE_SENT, ui_relationships.response_sent);

    // }}}

    // Create WebSocket connection.
    const socket = new WebSocket('ws://' + window.location.hostname + ':' + window.location.port + '/ws');

    // Connection opened
    socket.addEventListener('open', function(event) {
        ui_agent.connect();
    });

    // Listen for messages
    socket.addEventListener('message', function (event) {
        console.log('Routing: ' + event.data);
        msg = JSON.parse(event.data);
        msg_router.route(msg);
    });