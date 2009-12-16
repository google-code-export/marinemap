(function($){
    var KMLForest = {
        
        // options: {ge, gex, animate}
        _init: function(opts){
            if(this.options.ge && this.options.gex && this.options.div){
                this.ge = this.options.ge;
                this.gex = this.options.gex;
                this.div = this.options.div;
            }else{
                throw('Google earth instance, earth-api-utility-library instance, and/or map div not specified in options.');
            }
            this.element.addClass('marinemap-kml-forest');
            this.kmlObjects = {};
            var self = this;
            $(this.element).tree({animate: this.options.animate})
                .bind('itemToggle', function(e, clickedData, checked){
                    for(var i=0; i<clickedData.length; i++){
                        var node = clickedData[i];
                        if($(node).hasClass('toggle')){
                            var kml = $(node).data('kml');
                            kml.setVisibility(checked);
                        }
                    }
                })
                .bind('itemDoubleClick', function(e, target, ev){
                    var kml = target.data('kml');
                    if(kml.getType() == 'KmlTour'){
                        self.ge.getTourPlayer().setTour(kml);
                    }else{
                        // do something
                        var aspectRatio = $(this.div).width() / $(this.div).height();
                        self.gex.util.flyToObject(kml, {
                            boundsFallback: true,
                            aspectRatio: aspectRatio
                        });
                    }
                })
                .bind('itemClick', function(e, target, ev){
                    var kml = target.data('kml');
                    if(target.hasClass('description')){
                        target.find('input[checked=false]').click();
                        kml.setVisibility(true);
                        var balloon = self.ge.createFeatureBalloon('');
                        balloon.setFeature(kml);
                        balloon.setMinWidth(400);
                        self.ge.setBalloon(balloon);
                    }else{
                        self.ge.setBalloon(null);
                    }
                });
        },

        // options = {callback, cachebust, }
        add: function(url, opts){
            var options = opts || {};
            if(url in this.kmlObjects){
                throw('KML file with url '+url+' already added.');
            }
            var self = this;
            var original_url = url;
            var processKmlObject = function(kmlObject){
                if (!kmlObject) {
                    // show error
                    setTimeout(function() {
                        alert('Error loading KML - '+url);
                    },
                    0);
                    return;
                }
                self.kmlObjects[original_url] = kmlObject;
                self._addKmlObject(kmlObject, options.callback);
            }
            if(options.native_xhr){
                $.ajax({
                    url: url,
                    type: 'GET',
                    cache: !options.cachebust,
                    success: function(data, status){
                        var kmlObject = self.ge.parseKml(data);
                        processKmlObject(kmlObject);
                    },
                    error: function(){
                        processKmlObject();
                    },
                    dataType: 'html'
                });
            }else{
                // can be removed when the following ticket is resolved:
                // http://code.google.com/p/earth-api-samples/issues/detail?id=290&q=label%3AType-Defect&sort=-stars%20-status&colspec=ID%20Type%20Summary%20Component%20OpSys%20Browser%20Status%20Stars
                if(!url.match('http')){
                    url = window.location.protocol + "//" + window.location.host + "/" + url;
                    url = url.replace(/(\w)\/\//g, '$1/');
                }
                if(options.cachebust){
                    url = url + '?' + (new Date()).valueOf();
                }
                google.earth.fetchKml(this.ge, url, processKmlObject);                
            }
        },
                
        _addKmlObject: function(kmlObject, callback){
            this.ge.getFeatures().appendChild(kmlObject);
            this._buildTreeUI(kmlObject, callback);
        },
        
        _buildTreeUI: function(kmlObject, callback){
            var self = this;
            var topNode;
            this.gex.dom.walk({
                visitCallback: function(context){
                    var type = this.getType();
                    var child = $(self.element).tree('add', {
                        name: this.getName() || "No name specified in kml",
                        parent: context.current,
                        collapsible: !(this == kmlObject) && (type == 'KmlFolder' || type == 'KmlDocument' || type == 'KmlNetworkLink'),
                        open: this.getOpen(),
                        hideByDefault: false,
                        toggle: !(this == kmlObject),
                        classname: (this == kmlObject) ? 'marinemap-tree-category' : this.getType(),
                        checked: this.getVisibility(),
                        select: false,
                        snippet: this.getSnippet(),
                        doubleclick: true,
                        description: this.getDescription()
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
            if(!found){
                throw('Could not find node in kmlForest that represents the kml object.');
            }
            delete this.kmlObjects[url];
            this.gex.dom.removeObject(obj);
        },
        
        refresh: function(url, options){
            this.remove(url);
            this.add(url, options);
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
    };

    $.widget('marinemap.kmlForest', KMLForest);
    
    $.extend($.marinemap.kmlForest, {
        getter: ['getByUrl', 'length'],
        defaults: {
            animate: false,
             //matches google earth desktop behavior if set to false
            selectToggles: false
        }
    });
    
})(jQuery);
