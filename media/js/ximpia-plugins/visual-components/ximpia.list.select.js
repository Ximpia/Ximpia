/*
 * Ximpia Visual Component Input: Text, Password, etc...
 *
 */

(function($) {	

	$.fn.xpObjListSelect = function( method ) {  

        // Settings		
        var settings = {
        	excudeListSelect: ['type','id','element','help_text','label','data-xp-val', 'value', 'choices','choicesId'],
        	excludeListLabel: ['type','id','element'],
        	excludeList: ['info','type']
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
		render: function(data) {
			console.log($(this));
			console.log('Elements : ' + $(this).length);
			for (var i=0; i<$(this).length; i++) {
				console.log($(this)[i]);
				var element = $(this)[i]; 
				var idInputSrc = $(element).attr('id').split('_comp')[0];
				var idInput = $(element).attr('id').split('_comp')[0] + '_text';
				var idInputValue = $(element).attr('id').split('_comp')[0];
				var nameInput = idInputSrc.split('id_')[1];
				var idField = $(element).attr('id').split('_comp')[0] + '_field';
				$.metadata.setType("attr", "data-xp");
				var attrs = $(element).metadata();
				var dataAttrs = data[nameInput];
				console.log('XpObjListSelect...');
				console.log(dataAttrs);
				console.log(attrs);
				var type = 'text';
				var value = "";
				var choicesId = "";
				if (dataAttrs.hasOwnProperty('choicesId')) {
					choicesId = dataAttrs['choicesId'];
				}				
				if (attrs.hasOwnProperty('type')) {
					type = attrs.type;
				}
				// id, name, type
				var htmlContent = "";
				if (attrs.hasOwnProperty('left')) {
					htmlContent = "<div style=\"width: " + attrs['left'] + "px; float: left; border: 0px solid\"><label for=\"" + idInput + "\"></label>:</div> <div id=\"" + idField + "\" style=\"float: left; margin-top: 7px; margin-left: 3px\" ></div>";
				} else {
					htmlContent = "<div style=\"float: left; border: 0px solid\"><label for=\"" + idInput + "\"></label>:</div> <div id=\"" + idField + "\" style=\"float: left; margin-top: 7px; margin-left: 3px\" ></div>";
				}
				console.log(htmlContent);
				$(element).html(htmlContent);
				// Plugin
				var countryList = JSON.parse($('#id_choices').attr('value'))[choicesId];
				var results = {'results': []};
				for (j in countryList) {
					results['results'][j] = {'id': countryList[j][0], 'name': countryList[j][1]}
				}
				console.log('idField : ' + idField);
				var fb = $("#" + idField).flexbox(results,{
					autoCompleteFirstMatch: true,
					paging: false,
					maxVisibleRows: 6
				});
				//fb.setValue('es', 'Spain');
				// Input
				for (attr in dataAttrs) {
					var exists = ximpia.common.ArrayUtil.hasKey(settings.excudeListSelect, attr);
					if (exists == false) {
						value = dataAttrs[attr];
						$("#" + idInput).attr(attr, value);
					}					
				}
				for (attr in attrs) {
					var exists = ximpia.common.ArrayUtil.hasKey(settings.excludeList, attr);
					if (exists == false) {
						value = attrs[attr];
						$("#" + idInput).attr(attr, value);
					}					
				}
				// Label
				$("label[for=\"" + idInput + "\"]").text(dataAttrs['label']);
				if (attrs.info == true) {
					$("label[for=\"" + idInput + "\"]").addClass("info");
					// help_text
					if (dataAttrs.hasOwnProperty('help_text')) {
						$("label[for=\"" + idInput + "\"]").attr('data-xp-title', dataAttrs['help_text']);
					}
				}
				/*console.log($("#" + idInput));*/
				console.log($(element));
				console.log($('#id_country').val());
				console.log($('#id_country_input').val());
			}
		},
		disable: function() {
		},
		enable: function() {
		},
		setValue: function(code) {
			var countryList = JSON.parse($('#id_choices').attr('value'))[choicesId];
		}	
        };
		
        if ( methods[method] ) {
            return methods[ method ].apply( this, Array.prototype.slice.call( arguments, 1 ));
        } else if ( typeof method === 'object' || ! method ) {
            return methods.init.apply( this, arguments );
        } else {
            $.error( 'Method ' +  method + ' does not exist on jQuery.xpObjListSelect' );
        }    
		
	};

})(jQuery);
