var lingcod = {
    
    isnamespace_:true,
    
    init: function(){
        $('#panelManager').panelManager({top: '1em', left: 0});
        this.resize();
        var self = this;
        google.earth.createInstance(
            "map", 
            function(i){
                self.geInit(i);
            },
            function(code){
                self.geFailure(code);
            });
        this.setupListeners();
    },
    
    geInit: function(pluginInstance){
        ge = pluginInstance;
        ge.getWindow().setVisibility(true); // required
        gex = new GEarthExtensions(ge);
        
        this.googleLayers = new lingcod.map.googleLayers(ge, $('#ge_options'), $('#ge_layers'));
        this.geocoder = new lingcod.map.geocoder(gex, $('#flyToLocation'));
        this.measureTool = new lingcod.measureTool();
        this.drawTool = new lingcod.drawTool();
        var self = this;
        $('#measure_distance').click(function(){
            self.measureTool.clear();
            self.measureTool.measureDistance(gex, "distance");
        });
        $('#measure_area').click(function(){
            self.measureTool.clear();
            self.measureTool.measureArea(gex, "area");
        });
        $('#measure_clear').click(function(){
            self.measureTool.clear();
        });
        $('#measure_units').change(function(){
            self.measureTool.setUnits($(this).val());
        });
        $('#datalayerstree').kmlForest({ge: ge, gex: gex, div: $('#map')})
            .kmlForest('add', '/studyregion/kml/', {cachebust: true, callback: this.studyRegionLoaded})
            .kmlForest('add', window.public_data_layers, {cachebust: true});
        $('#mpa_draw').click(function(){
            document.getElementById("mpa_draw_results").innerHTML = '';
            self.drawTool.clear();
            self.drawTool.drawShape( gex, lingcod.drawMpaComplete ); 
        });
        $('#mpa_clear').click(function(){
            document.getElementById("mpa_draw_results").innerHTML = '';
            self.drawTool.clear();
        });
    },
    
    studyRegionLoaded: function(kmlObject, node){
        // Reorder so studyRegion is on top of the list
        $('#datalayerstree').prepend(node);
        if (kmlObject.getAbstractView()){
            ge.getView().setAbstractView(kmlObject.getAbstractView());
        }
        
    },
    
    geFailure: function(errorCode){
        alert("Failure loading the Google Earth Plugin: " + errorCode);
    },
    
    setupListeners: function(){
        var self = this;
        $(window).resize(function(){
            self.resize();
        });
    },
    
    resize: function(){
        var h = $(document.body).height() - $('#meta-navigation').outerHeight();
        $('#panelManager').height(h);
        var w = $(document.body).width() - $('#panelManager').width();
        $('#map_container').height(h).width(w);
        
        // $('#layout').height($(window).height())
        // $('#panelManager').panelManager('resize');
        // var size = [$(window).width(), $(window).height()];
        // var top_height = $('#meta-navigation').height();
        // var body_height = size[1] - top_height - 7;
        // var map_width = size[0] - $('.sidebar-panel').panel('width') - 20;
        // $('#map_container').height(body_height - 10);
        // $('.sidebar-panel').panel('resize', {height: body_height -10});
        // // $('div.sidebar-panel').height(body_height - 10);
        // $('#map_container').width(map_width - 10);
    }
};

