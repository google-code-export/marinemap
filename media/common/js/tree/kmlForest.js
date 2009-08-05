(function($){
    var KMLForest = {
        
        // options: {ge, gex, animate}
        _init: function(opts){
            if(this.options.ge && this.options.gex){
                this.ge = this.options.ge;
                this.gex = this.options.gex;                
            }else{
                throw('Google earth instance and/or earth-api-utility-library instance not specified in options.');
            }
            this.element.addClass('marinemap-kml-forest');
            this.kmlObjects = {};
            $(this.element).tree({animate: this.options.animate})
                .bind('itemToggle', function(e, clickedData, checked){
                    for(var i=0; i<clickedData.length; i++){
                        var node = clickedData[i];
                        
                        var kml = $(node).data('kml');
                        kml.setVisibility(checked);
                        var c = kml;
                        while (c && 'setVisibility' in c) {
                            c.setVisibility(checked);
                            c = c.getParentNode();
                            //store.setValue(item, 'checked' 
                        }
                    }
                });
        },

        // options = {callback, cachebust, }
        add: function(url, opts){
            if(url in this.kmlObjects){
                throw('KML file with url '+url+' already added.');
            }
            var original_url = url;
            var options = opts || {};
            var self = this;
            // can be removed when the following ticket is resolved:
            // http://code.google.com/p/earth-api-samples/issues/detail?id=290&q=label%3AType-Defect&sort=-stars%20-status&colspec=ID%20Type%20Summary%20Component%20OpSys%20Browser%20Status%20Stars
            if(!url.match('http')){
                url = window.location + url;
                url = url.replace(/(\w)\/\//g, '$1/');
            }
            if(options['cachebust']){
                url = url + '?' + (new Date).valueOf();
            }
            google.earth.fetchKml(this.ge, url,
            function(kmlObject) {
                if (!kmlObject) {
                    // show error
                    setTimeout(function() {
                        alert('Error loading KML.');
                    },
                    0);
                    return;
                }
                self.kmlObjects[original_url] = kmlObject;
                self._addKmlObject(kmlObject, options.callback);
            });            
        },
        
        _addKmlObject: function(kmlObject, callback){
            this.ge.getFeatures().appendChild(kmlObject);
            this._buildTreeUI(kmlObject, callback);
        },
        
        _buildTreeUI: function(kmlObject, callback){
            var self = this;
            var topNode;
            gex.dom.walk({
                visitCallback: function(context){
                    var type = this.getType();
                    var child = $(self.element).tree('add', {
                        name: this.getName() || "No name specified in kml",
                        parent: context.current,
                        collapsible: !(this == kmlObject) && (type == 'KmlFolder' || type == 'KmlDocument'),
                        open: this.getOpen(),
                        hideByDefault: false,
                        toggle: !(this == kmlObject),
                        classname: (this == kmlObject) ? 'marinemap-tree-category' : undefined,
                        checked: this.getVisibility(),
                        select: true,
                        snippet: this.getSnippet()
                    });
                    if(this == kmlObject){
                        topNode = child;
                    }
                    child.data('kml', this);
                    context.child = child;
                },
                rootContext: false,
                rootObject: kmlObject
            });
            if(callback){
                callback(kmlObject, topNode);
            }
        },
        
        clear: function(){
            for(var key in this.kmlObjects){
                this.remove(key);
            }
        },
        
        remove: function(url){
            var obj = this.kmlObjects[url];
            var found = false;
            $(this.element).find('> li').each(function(){
                if($(this).data('kml') == obj){
                    $(this).remove();
                    found = true;
                    return;
                }
            });
            if(!found)
                throw('Could not find node in kmlForest that represents the kml object.');
            delete this.kmlObjects[url];
            gex.dom.removeObject(obj);
        },
        
        refresh: function(kml){
        },
        
        getByUrl: function(url){
            if(this.kmlObjects[url]){
                return this.kmlObjects[url];
            }else{
                throw('Could not find kmlObject with that url.');
            }
        },
        
        length: function(){
            var length = 0;
            for(var key in this.kmlObjects){
                length += 1;
            }
            return length;
        }
    }

    $.widget('marinemap.kmlForest', KMLForest);
    
    $.extend($.marinemap.kmlForest, {
        getter: ['getByUrl', 'length'],
        defaults: {
            animate: false,
            selectToggles: false //matches google earth desktop behavior if set to false
        }
    });
    
})(jQuery);