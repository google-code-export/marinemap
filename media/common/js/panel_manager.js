(function($){
    $.widget("ui.panelManager", {
        _init: function() {
            this.stack = [];
            this.home = this.element.find('.sidebar-panel')[0];
            this.stack.push(this.home);
            this.index = 0;
            this._calculateStagingAreas();
            var self = this;
            this.element.find('a').live('click', function(e){
                e.preventDefault();
                if($(this).hasClass('back_link') || $(this).hasClass('backward')){
                    self._popPanel()
                }else{
                    self._appendPanel($(this));
                }
            });
        },
        
        createBackButton: function(){
            // get last panel in queue and create config options
        },

        createPanel: function(opts){
            opts.title = opts.title || 'Loading Panel...';
            var panel_opts = {
                width: this.element.width(),
                height: this.element.height(),
                hidden: true,
                html: 'spinner',
                title: opts.title
            };
            var panel = $('<div class="sidebar-panel" />')
            this.element.append(panel);
            panel.panel(panel_opts);
            this.stack.push(panel);
            return panel;
        },
        
        // Once the appropriate panels have been appended or popped,
        animateFromRight: function(callback){
            // Place in the waiting area on the right
            var incoming = $(this.stack[this.index]);
            var outgoing = $(this.stack[this.index - 1]);
            incoming.css('top', 0);
            incoming.css('left', this.stagingRightX);
            // Animate slide in
            var duration = 250;
            var easing = 'linear';
            var self = this;
            incoming.animate({
                top: 0,
                left: 0
            }, duration, easing, function(){
            });
            // Animate removal of old panel
            outgoing.animate({
                top: 0,
                left: this.element.width() * -1 - 10
            }, duration, easing, function(){
                $(this).hide();
                $(this.element).find('.back_link').fadeIn(500);
                if(callback){
                    callback(incoming, outgoing);
                }
            });
        },
        
        home: function(){
            return this.home;
        },
        
        resize: function(opts){
            opts = opts || {};
            this.element.find('.sidebar-panel').panel('resize', opts);
            opts.width = opts.width || this.element.width();
            opts.height = opts.height || this.element.find('.sidebar-panel').height();
            this.element.width(opts.width);
            this.element.height(opts.height);
            this._calculateStagingAreas();
        },
        
        // Calculates where to place panels before they are slid into view
        _calculateStagingAreas: function(){
            var position = this.element.position();
            var $sp = this.element.find('.sidebar-panel');
            this.stagingTop = position.top;
            this.stagingLeftX = position.left - $sp.width();
            this.stagingRightX = position.left + $sp.width() + 10;
        },
        
        // Show a panel, sliding it in from the right and adding to the stack
        _appendPanel: function(link){
            var panel = this.createPanel({title: $(link).attr('title')});
            this.resize();
            var self = this;
            this.index = this.index + 1;
            this.animateFromRight();
            $.ajax({
                url: $(link).attr('href'),
                success: function(data, s){
                    self._appendSuccess(data, s);
                },
                error: function(s){
                    self._appendFail
                },
                method: 'GET'
            });
            return panel;
        },
        
        _appendSuccess: function(data, s){
            var panel = $(this.stack[this.index]);
            var html = $(data).find('.sidebar-panel').html();
            var back = $(data).find('.back_link');
            if(!back.length){
                back = this.createBackButton();
            }
            $(panel).panel('setContent', $(data).find('.sidebar-panel').html());
            $(panel).panel('resize');            
            
            $(this.element).find('.back_link').remove();
            $(this.element).append(back);
            back.hide();
        },
        
        _appendFail: function(s){
            alert('loading of panel content failed. ' + s);
        },

        destroy: function(){
            $.widget.prototype.apply(this, arguments); // default destroy
            this.element.remove();
        }
    });

    $.extend($.ui.panelManager, {
        getter: "home createPanel",
        defaults: {
            width: 360,
            height: 400
        }
    });
})(jQuery);
