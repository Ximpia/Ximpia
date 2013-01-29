/*
 * List of content elements
 * 
 * TODO: Include the html for component
 *
 */

(function($) {	

	$.fn.xpObjListContent = function( method ) {  

        // Settings		
        var settings = {
        };
        
        var methods = {
		init : function( options ) { 
                	return this.each(function() {        
                    		// If options exist, lets merge them
                    		// with our default settings
                    		if ( options ) { 
	                        	$.extend( settings, options );
                    		}
                	});
		},
		render : function() {
			
		}
        };
		
        if ( methods[method] ) {
            return methods[ method ].apply( this, Array.prototype.slice.call( arguments, 1 ));
        } else if ( typeof method === 'object' || ! method ) {
            return methods.init.apply( this, arguments );
        } else {
            $.error( 'Method ' +  method + ' does not exist on jQuery.xpObjListContent' );
        }    
		
	};

})(jQuery);
