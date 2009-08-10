/**
 * Constructor for googleLayers widget which controls the display options of the plugin.
 * @constructor
 * @param {GEPlugin} plugin Reference to the google earth plugin instance.
 * @param {HTMLFormElement} options The form that controls options. See <a href="http://code.google.com/apis/earth/documentation/reference/interface_g_e_options.html">GEOptions</a>
 * @param {HTMLFormElement} layers The form that controls which layers are displayed. See <a href="http://code.google.com/apis/earth/documentation/layers.html#layers">layer reference</a>
 */
lingcod.map.googleLayers = function(ge, options_form, layers_form){
    this.layers = $(layers_form);
    this.options = $(options_form);
    this.get = ge;
    var self = this;
    $(this.layers).find('input').click(function(){
        self.updateLayers();
    });
    
    $(this.options).find('input').click(function(){
        self.updateOptions();
    });
    
    this.updateLayers();
    this.updateOptions();
}

/**
 * Looks at the layers form and updates the map to match form values
 */
lingcod.map.googleLayers.prototype.updateLayers = function(){
    this.layers.find('input').each(function(){
        ge.getLayerRoot().enableLayerById(ge[$(this).attr('name')], $(this).attr('checked'));
    });
};

/**
 * Looks at the options form and updates the map to match form values. The 
 * name of the input element should match the setXVisibility function on 
 * ge.getOptions();.
 * for example:
 *
 *      &lt;input name=&quot;setGridVisibility&quot; /&gt;
 */
lingcod.map.googleLayers.prototype.updateOptions = function(){
    var options = ge.getOptions();
    this.options.find('input').each(function(){
        var $input = $(this);
        var name = $input.attr('name');
        if(name != 'nav' && name != 'sun'){
            options[name](this.checked);
        }
    });
    
    if(this.options.find('input[name="nav"]').length){
        if (this.options.find('input[name="nav"]:checked').length) {
            ge.getNavigationControl().setVisibility(ge.VISIBILITY_SHOW);
        }else{
            ge.getNavigationControl().setVisibility(ge.VISIBILITY_HIDE);
        }
    }
    
    if(this.options.find('input[name="sun"]').length){
        if(this.options.find('input[name="sun"]:checked').length){
            ge.getSun().setVisibility(true);
        }else{
            ge.getSun().setVisibility(false);
        }
    }
};

/**
 * Unbinds all event listeners.
 */ 
lingcod.map.googleLayers.prototype.destroy = function(){
    $(this.layers).find('input').unbind('click');
    $(this.options).find('input').unbind('click');
}