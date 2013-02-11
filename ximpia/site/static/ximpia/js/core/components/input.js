/*
 * Ximpia Visual Component Input: Text, Password, Decimal, etc... with autocompletion support
 *
 * 
 * ** Attributes **
 * 
 * ** Attributes for Autocompletion Choices (data-xp-complete) **
 *
 * * ``choicesId``
 * * ``choiceDisplay`` [optional] default:value : name|value. Display either name or value from choices.
 * * ``maxHeight`` [optional]
 * * ``minCharacters`` [optional]
 * 
 * ** Attributes for Autocompletion Server (data-xp-complete) **
 *
 * * ``app`` [optional]
 * * ``dbClass``
 * * ``searchField`` :String : Search field to match for text from input field.
 * * ``maxHeight`` [optional]
 * * ``minCharacters`` [optional]
 * * ``params`` [optional] :Object : Parameters to filter completion list.
 * * ``fieldValue`` [optional] :String : Field to show results. In case not defined, will use the model string representation.
 * * ``extraFields`` [optional] :List : Fields to show in extra Object
 * 
 * ** Methods **
 * 
 * * ``render``
 * * ``complete``
 * * ``enable``
 * * ``disable``
 * * ``unrender``
 * 
 * ** Interfaces **
 * 
 * IComplete, IInputField
 * 
 */

(function($) {	

	$.fn.xpField = function( method ) {
		
	// Include documentation from wiki here  

        // Settings		
        var settings = {
        	excudeListInput: ['type','id','element','help_text','label','left'],
        	excudeListInputSug: ['type','id','element','help_text','label','left'],
        	excludeListLabel: ['type','id','element'],
        	excludeList: ['info','type','left'],
        	htmlAttrs: ['tabindex','readonly','maxlength','class','value','name','autocomplete','size'],
        	djangoAttrs: ['type','id','info','help_text','label','element','left','xptype'],
        	reRender: false,
        	labelPosition: 'left',
        	choiceDisplay: 'value'
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
		render: function(xpForm) {
			ximpia.console.log('input :: renderField...');
			var data = ximpia.common.Browser.getFormDataFromSession(xpForm);
			ximpia.console.log(data);
			for (var i=0; i<$(this).length; i++) {
				ximpia.console.log($(this)[i]);
				var element = $(this)[i]; 
				var idInput = $(element).attr('id').split('_comp')[0];
				var doRender = ximpia.common.Form.doRender(element, settings.reRender);
				if (doRender == true) {
					ximpia.console.log('renderField :: id: ' + $(element).attr('id'));
					var nameInput = idInput.split('id_')[1];
					ximpia.console.log('nameInput: ' + nameInput);
					$.metadata.setType("attr", "data-xp");
					var attrs = $(element).metadata();
					//ximpia.console.log('input attrs: ' + idInput);
					//ximpia.console.log(attrs);
					var relatedId = $(element).attr('data-xp-related');
					var elementType = $(element).attr('data-xp-type');
					var dataAttrs = data[nameInput];
					var type = 'text';
					if (attrs.hasOwnProperty('type')) {
						type = attrs.type;
					}
					if (!attrs.hasOwnProperty('labelPosition')) {
						attrs['labelPosition'] = settings.labelPosition;
					}
					// id, name, type
					var htmlContent = "";
					ximpia.console.log(dataAttrs);
					var myValue = dataAttrs.value;
					if (attrs['labelPosition'] == 'top') {
						htmlContent = "<label for=\"" + idInput + "\"></label><br/><input id=\"" + idInput + "\" type=\"" + type + "\" name=\"" + 
							nameInput + "\" value=\"" + myValue + "\" />";						
					} else {
						htmlContent = "<label for=\"" + idInput + "\"></label><input id=\"" + idInput + "\" type=\"" + type + "\" name=\"" + 
							nameInput + "\" value=\"" + myValue + "\" />";					
					}
					$(element).html(htmlContent);
					$(element).attr('data-xp-render', JSON.stringify(true));
					// Input
					// Insert attributes to form element from server and metadata of visual component
					ximpia.common.Form.doAttributes({
						djangoAttrs: settings.djangoAttrs,
						htmlAttrs: settings.htmlAttrs,
						excludeList: settings.excludeList,
						dataAttrs: dataAttrs,
						attrs: attrs,
						idElement: idInput
					});
					if (typeof relatedId != 'undefined') {
						$("#" + idInput).attr('data-xp-related', relatedId);
					}
					if (typeof elementType != 'undefined') {
						$("#" + idInput).attr('data-xp-type', elementType);
					}
					//ximpia.console.log($("#" + idInput));
					// Label
					//ximpia.console.log('dataAttrs');
					//ximpia.console.log(dataAttrs);
					if (!attrs.hasOwnProperty('hasLabel')) {
						attrs['hasLabel'] = true;
					}
					if (attrs['labelPosition'] == 'left' && attrs['hasLabel'] == true) {
						$("label[for=\"" + idInput + "\"]").addClass("labelSep");
					}
					if (typeof dataAttrs != 'undefined' && dataAttrs.hasOwnProperty('label') && attrs['hasLabel'] == true) {
						if (attrs.hasOwnProperty('label')) {
							$("label[for=\"" + idInput + "\"]").text(attrs['label']);
						} else {
							$("label[for=\"" + idInput + "\"]").text(dataAttrs['label']);
						}
						if (attrs.info == true) {
							$("label[for=\"" + idInput + "\"]").addClass("info");
							// help_text
							if (dataAttrs.hasOwnProperty('helpText')) {
								$("label[for=\"" + idInput + "\"]").attr('data-xp-title', dataAttrs['helpText']);
							}
						}
					}
					// Autocompletion
					$(element).xpField('complete', xpForm);
				}
			}
		},
		complete: function() {
        	// Autocompletion
			for (var i=0; i<$(this).length; i++) {
				ximpia.console.log($(this)[i]);
				var element = $(this)[i];         	
				$.metadata.setType("attr", "data-xp-complete");
				var attrs = $(element).metadata();
				ximpia.console.log('xpField.complete ::  attrs...');
				ximpia.console.log(attrs);
				var hasComplete = true;
				var idInput = $(element).attr('id').split('_comp')[0];
				ximpia.console.log('xpField.complete :: idInput: ' + idInput);
				if (typeof(attrs) == 'undefined') {
					hasComplete = false;
				}
				if (hasComplete == true) {
					ximpia.console.log('xpField.complete ::  Autocomplete...');
					// maxHeight
					var maxHeight = ximpia.settings.COMPLETE_MAX_HEIGHT;
					if (attrs.hasOwnProperty('maxHeight')) {
						maxHeight = attrs['maxHeight'];
					}
					// minCharacters
					var minCharacters = ximpia.settings.COMPLETE_MIN_CHARACTERS;
					if (attrs.hasOwnProperty('minCharacters')) {
						minCharacters = attrs['minCharacters'];
					}
					if (attrs.hasOwnProperty('choicesId')) {
						// From choices...
						ximpia.console.log('xpField.complete :: Autocomplete from choices...');
						var choicesId = attrs['choicesId'];
						var choices = JSON.parse($("input[name='choices']").attr('value'))[choicesId];
						var sugData = {};
						if (typeof(choices) != 'undefined') {
							sugData = []
						}
						if (!attrs.hasOwnProperty('choiceDisplay')) {
							attrs['choiceDisplay'] = settings.choiceDisplay;
						}
						for (choiceIndex in choices) {
							sugData[choiceIndex] = {}
							sugData[choiceIndex]['id'] = choices[choiceIndex][0];
							if (attrs['choiceDisplay'] == 'value') {
								sugData[choiceIndex]['text'] = choices[choiceIndex][1];
							} else {
								sugData[choiceIndex]['text'] = choices[choiceIndex][0];
							}
						}
						ximpia.console.log('xpField.complete :: Autocomplete :: sugData...');
						ximpia.console.log(sugData);
						$("#" + idInput).jsonSuggest({	data: sugData, 
														maxHeight: maxHeight, 
														minCharacters: minCharacters
														});
					} else if(attrs.hasOwnProperty('dbClass')) {
						// From server...
						ximpia.console.log('xpField.complete :: Autocomplete from server...');
						var app = ximpia.common.Browser.getApp();
						if (attrs.hasOwnProperty('app')) {
							app = attrs['app']
						}
						var params = {};
						if (attrs.hasOwnProperty('params')) {
							params = eval("(" + attrs['params'] + ")");
						}
						var dbClass = attrs['dbClass'];
						url = '/jxSuggestList?app=' + app + '&dbClass=' + dbClass + '&searchField=' + attrs['searchField'];
						if (Object.keys(params).length != 0) {
							url += "&params=" + JSON.stringify(params);
						}
						if (attrs.hasOwnProperty('fieldValue')) {
							url += "&fieldValue=" + attrs['fieldValue'];
						}
						if (attrs.hasOwnProperty('extraFields')) {
							url += "&extraFields=" + JSON.stringify(attrs['extraFields'])
						}
						$("#" + idInput).jsonSuggest({	url: url, 
														maxHeight: maxHeight, 
														minCharacters: minCharacters
													});
					}						
				}
			}
		},
		disable: function() {
			/*var idInput = $(this).attr('id').split('_comp')[0];
			$("#" + idInput).attr('disable', 'disable');*/
			for (var i=0; i<$(this).length; i++) {
				// Get all option items and disable them
				$(this).find("input[data-xp-type='field']").each(function() {
					$(this).attr('disabled', true);
				})				
			}
		},
		enable: function() {
			for (var i=0; i<$(this).length; i++) {
				// Get all option items and disable them
				$(this).find("input[data-xp-type='field']").each(function() {
					$(this).attr('disabled', false);
				})				
			}
		},
		unrender: function() {
			for (var i=0; i<$(this).length; i++) {
				$(this).empty();
				$(this).removeAttr('data-xp-render');
			}
		}
		};		
        if ( methods[method] ) {
            return methods[ method ].apply( this, Array.prototype.slice.call( arguments, 1 ));
        } else if ( typeof method === 'object' || ! method ) {
            return methods.init.apply( this, arguments );
        } else {
            $.error( 'Method ' +  method + ' does not exist on jQuery.xpField' );
        }    
		
	};

})(jQuery);


/*
 * Ximpia Visual Component Input: Text, Password, Decimal, etc... with autocompletion support
 *
 * 
 * ** Attributes **
 * 
 * 
 * ** Methods **
 * 
 */

(function($) {	

	$.fn.xpFieldNumber = function( method ) {
		
	// Include documentation from wiki here  

        // Settings		
        var settings = {
        	excudeListInput: ['type','id','element','help_text','label','left'],
        	excudeListInputSug: ['type','id','element','help_text','label','left'],
        	excludeListLabel: ['type','id','element'],
        	excludeList: ['info','type','left'],
        	htmlAttrs: ['tabindex','readonly','maxlength','class','value','name','autocomplete','size'],
        	djangoAttrs: ['type','id','info','help_text','label','element','left','xptype'],
        	reRender: false,
        	labelPosition: 'left',
        	hasAutocompletion: false
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
		render: function(xpForm) {
			ximpia.console.log('input :: renderField...');
			var data = ximpia.common.Browser.getFormDataFromSession(xpForm);
			ximpia.console.log(data);
			for (var i=0; i<$(this).length; i++) {
				ximpia.console.log($(this)[i]);
				var element = $(this)[i]; 
				var idInput = $(element).attr('id').split('_comp')[0];
				var doRender = ximpia.common.Form.doRender(element, settings.reRender);
				if (doRender == true) {
					ximpia.console.log('renderField :: id: ' + $(element).attr('id'));
					var nameInput = idInput.split('id_')[1];
					ximpia.console.log('nameInput: ' + nameInput);
					$.metadata.setType("attr", "data-xp");
					var attrs = $(element).metadata();
					//ximpia.console.log('input attrs: ' + idInput);
					//ximpia.console.log(attrs);
					var relatedId = $(element).attr('data-xp-related');
					var elementType = $(element).attr('data-xp-type');
					var dataAttrs = data[nameInput];
					var type = 'text';
					if (attrs.hasOwnProperty('type')) {
						type = attrs.type;
					}
					if (!attrs.hasOwnProperty('labelPosition')) {
						attrs['labelPosition'] = settings.labelPosition;
					}
					// id, name, type
					var htmlContent = "";
					ximpia.console.log(dataAttrs);
					var myValue = dataAttrs.value;
					if (attrs['labelPosition'] == 'top') {
						htmlContent = "<label for=\"" + idInput + "\"></label><br/><input id=\"" + idInput + "\" type=\"" + type + "\" name=\"" + 
							nameInput + "\" value=\"" + myValue + "\" />";						
					} else {
						htmlContent = "<label for=\"" + idInput + "\"></label><input id=\"" + idInput + "\" type=\"" + type + "\" name=\"" + 
							nameInput + "\" value=\"" + myValue + "\" />";					
					}
					$(element).html(htmlContent);
					$(element).attr('data-xp-render', JSON.stringify(true));
					// Input
					// Insert attributes to form element from server and metadata of visual component
					ximpia.common.Form.doAttributes({
						djangoAttrs: settings.djangoAttrs,
						htmlAttrs: settings.htmlAttrs,
						excludeList: settings.excludeList,
						dataAttrs: dataAttrs,
						attrs: attrs,
						idElement: idInput
					});
					if (typeof relatedId != 'undefined') {
						$("#" + idInput).attr('data-xp-related', relatedId);
					}
					if (typeof elementType != 'undefined') {
						$("#" + idInput).attr('data-xp-type', elementType);
					}
					//ximpia.console.log($("#" + idInput));
					// Label
					//ximpia.console.log('dataAttrs');
					//ximpia.console.log(dataAttrs);
					if (!attrs.hasOwnProperty('hasLabel')) {
						attrs['hasLabel'] = true;
					}
					if (attrs['labelPosition'] == 'left' && attrs['hasLabel'] == true) {
						$("label[for=\"" + idInput + "\"]").addClass("labelSep");
					}
					if (typeof dataAttrs != 'undefined' && dataAttrs.hasOwnProperty('label') && attrs['hasLabel'] == true) {
						if (attrs.hasOwnProperty('label')) {
							$("label[for=\"" + idInput + "\"]").text(attrs['label']);
						} else {
							$("label[for=\"" + idInput + "\"]").text(dataAttrs['label']);
						}
						if (attrs.info == true) {
							$("label[for=\"" + idInput + "\"]").addClass("info");
							// help_text
							if (dataAttrs.hasOwnProperty('helpText')) {
								$("label[for=\"" + idInput + "\"]").attr('data-xp-title', dataAttrs['helpText']);
							}
						}
					}
					// spinner for numbers
					var spinObj = {};
					if (dataAttrs.hasOwnProperty('maxValue')) {
						spinObj['max'] = dataAttrs['maxValue'];
					}
					if (dataAttrs.hasOwnProperty('minValue')) {
						spinObj['min'] = dataAttrs['minValue'];
					}
					if (dataAttrs['fieldType'] == 'IntegerField') {
						spinObj.step = 1;
						spinObj.numberFormat = 'n';
						$('#' + idInput).spinner(spinObj);
					} else if (dataAttrs['fieldType'] == 'FloatField') {
						spinObj.step = 1;
						spinObj.numberFormat = 'n';
						$('#' + idInput).spinner(spinObj);
					} else if (dataAttrs['fieldType'] == 'DecimalField' && dataAttrs.hasOwnProperty('decimalPlaces')) {
						spinObj.numberFormat = 'n';
						spinObj.step = 1/(dataAttrs['decimalPlaces']*10);
						$('#' + idInput).spinner(spinObj);
					}
				}
			}
		},
		disable: function() {
			/*var idInput = $(this).attr('id').split('_comp')[0];
			$("#" + idInput).attr('disable', 'disable');*/
			for (var i=0; i<$(this).length; i++) {
				// Get all option items and disable them
				$(this).find("input[data-xp-type='field']").each(function() {
					$(this).attr('disabled', true);
				})				
			}
		},
		enable: function() {
			for (var i=0; i<$(this).length; i++) {
				// Get all option items and disable them
				$(this).find("input[data-xp-type='field']").each(function() {
					$(this).attr('disabled', false);
				})				
			}
		},
		unrender: function() {
			for (var i=0; i<$(this).length; i++) {
				$(this).empty();
				$(this).removeAttr('data-xp-render');
			}
		}
		};		
        if ( methods[method] ) {
            return methods[ method ].apply( this, Array.prototype.slice.call( arguments, 1 ));
        } else if ( typeof method === 'object' || ! method ) {
            return methods.init.apply( this, arguments );
        } else {
            $.error( 'Method ' +  method + ' does not exist on jQuery.xpFieldNumber' );
        }    
		
	};

})(jQuery);


/*
 * Ximpia Field Check
 * 
 * Renders fields that are BooleanField, with values true / false or 1 for true and 0 for false
 * 
 * Support labels. Check control can be before label or after.
 * 
 * <div id="id_hasUrl_comp" data-xp-type="field.check" data-xp="{}" > </div>
 *
 * ** Attributes (data-xp) **
 * 
 * * ``label`` [optional] : Field label
 * * ``controlPosition`` [optional] : 'before'|'after'. Default: 'before'. Position for the radio control, after or before text. 
 * 
 * ** Interfaces **
 * 
 * This components implements these interfaces:
 * 
 * * ``IInputField``
 * 
 * ** Methods **
 * 
 * * ``render``
 * * ``disable``
 * * ``enable``
 * 
 * 
 */

(function($) {	

	$.fn.xpFieldCheck = function( method ) {
		
	// Include documentation from wiki here  

        // Settings		
        var settings = {
        	controlPosition: 'after',
        	excudeListInput: ['type','id','element','help_text','label','left'],
        	excudeListInputSug: ['type','id','element','help_text','label','left'],
        	excludeListLabel: ['type','id','element'],
        	excludeList: ['info','type','left'],
        	htmlAttrs: ['tabindex','maxlength','readonly','class','value','name'],
        	djangoAttrs: ['type','id','info','help_text','label','element','left','xptype'],
        	isRender: false
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
		render: function(xpForm) {
			/**
			 * Render for radio buttons
			 */
			// id_month_comp : choiceId:'months'
			ximpia.console.log('xpOption :: option ... render...');
			var data = ximpia.common.Browser.getFormDataFromSession(xpForm);
			ximpia.console.log(data);
			for (var i=0; i<$(this).length; i++) {
				var element = $(this)[i];
				ximpia.console.log('xpOption :: element : ' + element); 
				var idBase = $(element).attr('id').split('_comp')[0];
				var name = idBase.split('id_')[1];
				ximpia.console.log('xpOption :: idBase : ' + idBase);
				var hasToRender = ximpia.common.Form.hasToRender(element, settings.reRender);
				if (hasToRender == true && data.hasOwnProperty(name)) {					
					var value = "";
					var choicesId = "";
					value = data[name]['value'];
					$.metadata.setType("attr", "data-xp");
					var attrs = $(element).metadata();
					ximpia.console.log('xpFieldCheck.render :: attrs...');
					ximpia.console.log(attrs);
	        		var htmlContent = "";
	        		if (!attrs.hasOwnProperty('controlPosition')) {
	        			attrs['controlPosition'] = settings.controlPosition;
	        		}
	        		// Label:
	        		var label = data[name]['label'];
	        		if (attrs.hasOwnProperty('label')) {
	        			label = attrs['label'];
	        		}
					var controlHtml = "";
					var ctlId = "id_" + name;
					if (value == true || value == '1') {
						controlHtml += "<input id=\"" + ctlId + "\" type=\"checkbox\" data-xp-type=\"field.check\" name=\"" + name + 
							"\" value=\"\" data-xp=\"{}\" checked=\"checked\"";
					} else {
						controlHtml += "<input id=\"" + ctlId + "\" type=\"checkbox\" data-xp-type=\"field.check\" name=\"" + name + 
							"\" value=\"\" data-xp=\"{}\"";
					}
					controlHtml += "/>";
        			var helpText = "";
        			if (attrs.hasOwnProperty('info') && attrs.info == true && data[name].hasOwnProperty('helpText') && 
        						attrs['controlPosition'] == 'after') {
        				helpText = "data-xp-title=\"" + data[name]['helpText'] + "\""
        			}
        			var attrClass = "";
        			if (attrs.hasOwnProperty('info') && attrs.info == true) {
        				attrClass = "class=\"info\"";
        			}
					if (attrs['controlPosition'] == 'before') {
						htmlContent += controlHtml + "<label for=\"" + ctlId + "\"" + attrClass + ' ' + helpText + ">" + 
							label + "</label>";
					} else {
						htmlContent += "<label for=\"" + ctlId + "\"" + attrClass + ' ' + helpText + ">" + label + ": </label>" + 
							controlHtml;
					}
					// Assign html visual component div element
					$(element).html(htmlContent);
					// Help text...
					// Set render, since we have rendered visual component					
					ximpia.common.Form.doAttributes({
						djangoAttrs: settings.djangoAttrs,
						htmlAttrs: settings.htmlAttrs,
						excludeList: settings.excludeList,
						dataAttrs: data[name],
						attrs: attrs,
						idElement: idBase
					});
					if (typeof relatedId != 'undefined') {
						$("#" + idInput).attr('data-xp-related', relatedId);
					}					
					$(element).attr('data-xp-render', JSON.stringify(true));
					// Trace
					ximpia.console.log(htmlContent);
				} else if (!data.hasOwnProperty(name)) {
					ximpia.console.log('xpOption.render :: server data has no variable');
				}
			}
		},
		disable: function() {
			for (var i=0; i<$(this).length; i++) {
				// Get all option items and disable them
				$(this).find("input[data-xp-type='field.check']").each(function() {
					$(this).attr('disabled', true);
				})				
			}
		},
		enable: function() {
			for (var i=0; i<$(this).length; i++) {
				// Get all option items and disable them
				$(this).find("input[data-xp-type='field.check']").each(function() {
					$(this).attr('disabled', false);
				})				
			}
		},
		unrender: function() {
			for (var i=0; i<$(this).length; i++) {
				$(this).empty();
				$(this).removeAttr('data-xp-render');
			}
		}
        };
		
        if ( methods[method] ) {
            return methods[ method ].apply( this, Array.prototype.slice.call( arguments, 1 ));
        } else if ( typeof method === 'object' || ! method ) {
            return methods.init.apply( this, arguments );
        } else {
            $.error( 'Method ' +  method + ' does not exist on jQuery.xpFieldCheck' );
        }    
		
	};

})(jQuery);


/*
 * Date and Time field representation. This component renders form fields Date, DateTime and Time.
 * 
 * When field type is Date, a date tooltip will popup to select date.
 * 
 * When field type is Time, a time tooltip will popup to select time with two selection bars for hour and minute.
 * 
 * When field type is DateTime, a date with time tooltip will show up with calendar and time bars.
 *
 * <div id="id_updateDate_comp" data-xp-type="field.datetime" data-xp="{}"> </div>
 * 
 * We need to render the input field like Field, then apply the correct plugin depending on format: date, time or datetime
 * 
 * ** Attributes **
 * 
 * * ``hasLabel``
 * * ``labelPosition``
 * * ``info``
 * * ``class``
 * * ``tabindex``
 * * ``readonly``
 * * ``maxlength``
 * * ``value``
 * * ``name``
 * * ``autocomplete``
 * 
 * ** Methods **
 * 
 * * ``render``
 * * ``disable``
 * * ``enable``
 * * ``unrender``
 * 
 */

(function($) {	

	$.fn.xpFieldDateTime = function( method ) {

        // Settings		
        var settings = {
        	excudeListInput: ['type','id','element','help_text','label','left'],
        	excudeListInputSug: ['type','id','element','help_text','label','left'],
        	excludeListLabel: ['type','id','element'],
        	excludeList: ['info','type','left'],
        	htmlAttrs: ['tabindex','maxlength','class','value','name','autocomplete'],
        	djangoAttrs: ['type','id','info','help_text','label','element','left','xptype'],
        	reRender: false,
        	labelPosition: 'left'
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
		render : function(xpForm) {
			ximpia.console.log('xpFieldDateTime.render ...');
			var data = ximpia.common.Browser.getFormDataFromSession(xpForm);
			ximpia.console.log(data);
			for (var i=0; i<$(this).length; i++) {
				ximpia.console.log($(this)[i]);
				var element = $(this)[i]; 
				var idInput = $(element).attr('id').split('_comp')[0];
				var doRender = ximpia.common.Form.doRender(element, settings.reRender);
				if (doRender == true) {
					ximpia.console.log('xpFieldDateTime.render :: id: ' + $(element).attr('id'));
					var nameInput = idInput.split('id_')[1];
					ximpia.console.log('xpFieldDateTime.render :: nameInput: ' + nameInput);
					$.metadata.setType("attr", "data-xp");
					var attrs = $(element).metadata();
					var relatedId = $(element).attr('data-xp-related');
					var elementType = $(element).attr('data-xp-type');
					var dataAttrs = data[nameInput];
					var type = 'text';
					if (attrs.hasOwnProperty('type')) {
						type = attrs.type;
					}
					if (!attrs.hasOwnProperty('labelPosition')) {
						attrs['labelPosition'] = settings.labelPosition;
					}
					// id, name, type					
					var htmlContent = "";
					ximpia.console.log(dataAttrs);
					var myValue = dataAttrs.value;
					if (attrs['labelPosition'] == 'top') {
						htmlContent = "<label for=\"" + idInput + "\"></label><br/><input id=\"" + idInput + "\" type=\"" + type + 
									"\" name=\"" + nameInput + "\" value=\"" + myValue + "\" readonly=\"readonly\" />";
						
					} else {
						htmlContent = "<label for=\"" + idInput + "\"></label><input id=\"" + idInput + "\" type=\"" + type + 
									"\" name=\"" + nameInput + "\" value=\"" + myValue + "\" readonly=\"readonly\" />";
						
					}
					$(element).html(htmlContent);					
					// Input
					// Insert attributes to form element from server and metadata of visual component
					ximpia.common.Form.doAttributes({
						djangoAttrs: settings.djangoAttrs,
						htmlAttrs: settings.htmlAttrs,
						excludeList: settings.excludeList,
						dataAttrs: dataAttrs,
						attrs: attrs,
						idElement: idInput
					});
					if (typeof relatedId != 'undefined') {
						$("#" + idInput).attr('data-xp-related', relatedId);
					}
					$("#" + idInput).attr('data-xp-type', 'field.datetime');
					// Label
					if (!attrs.hasOwnProperty('hasLabel')) {
						attrs['hasLabel'] = true;
					}
					if (attrs['labelPosition'] == 'left' && attrs['hasLabel'] == true) {
						$("label[for=\"" + idInput + "\"]").addClass("labelSep");
					}
					if (typeof dataAttrs != 'undefined' && dataAttrs.hasOwnProperty('label') && attrs['hasLabel'] == true) {
						if (attrs.hasOwnProperty('label')) {
							$("label[for=\"" + idInput + "\"]").text(attrs['label']);
						} else {
							$("label[for=\"" + idInput + "\"]").text(dataAttrs['label']);
						}
						if (attrs.info == true) {
							$("label[for=\"" + idInput + "\"]").addClass("info");
							// help_text
							if (dataAttrs.hasOwnProperty('helpText')) {
								$("label[for=\"" + idInput + "\"]").attr('data-xp-title', dataAttrs['helpText']);
							}
						}
					}
					if (dataAttrs['fieldType'] == 'DateField') {			
						$('#' + idInput).datepicker();
					} else if (dataAttrs['fieldType'] == 'DateTimeField') {
						$('#' + idInput).datetimepicker();
					} else if (dataAttrs['fieldType'] == 'TimeField') {
						$('#' + idInput).timepicker();
					}
					$(element).attr('data-xp-render', JSON.stringify(true));
				}
			}
		},
		disable: function() {
			for (var i=0; i<$(this).length; i++) {
				// Get all option items and disable them
				$(this).find("input[data-xp-type='field.date']").each(function() {
					$(this).attr('disabled', true);
				})				
			}
		},
		enable: function() {
			for (var i=0; i<$(this).length; i++) {
				// Get all option items and disable them
				$(this).find("input[data-xp-type='field.date']").each(function() {
					$(this).attr('disabled', false);
				})				
			}
		},
		unrender: function() {
			for (var i=0; i<$(this).length; i++) {
				$(this).empty();
				$(this).removeAttr('data-xp-render');
			}
		}
		};		
        if ( methods[method] ) {
            return methods[ method ].apply( this, Array.prototype.slice.call( arguments, 1 ));
        } else if ( typeof method === 'object' || ! method ) {
            return methods.init.apply( this, arguments );
        } else {
            $.error( 'Method ' +  method + ' does not exist on jQuery.xpFieldDateTime' );
        }
	};

})(jQuery);



/*
 * Ximpia Visual Component Hidden
 * 
 * TODO: Include the html for component
 *
 */

(function($) {	

	$.fn.xpHidden = function( method ) {
		
	// Include documentation from wiki here  

        // Settings		
        var settings = {
        	excudeListInput: ['type','id','element','help_text','label','left'],
        	excudeListInputSug: ['type','id','element','help_text','label','left'],
        	excludeListLabel: ['type','id','element'],
        	excludeList: ['info','type','left'],
        	htmlAttrs: ['tabindex','readonly','maxlength','class','value','name','autocomplete'],
        	djangoAttrs: ['type','id','info','help_text','label','element','left','xptype'],
        	reRender: false
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
		addHidden: function(xpForm) {
			// xpData.form_login
			//ximpia.console.log('addHidden...');
			//ximpia.console.log('xpForm: ', xpForm);
			var data = ximpia.common.Browser.getFormDataFromSession(xpForm);
			var formId = ximpia.common.Browser.getForm(xpForm);
			var viewName = ximpia.common.Browser.getView(xpForm);
			//ximpia.console.log('data length : ' + data.length());
			if (typeof data != 'undefined') {
				var list = Object.keys(data);
				//JSON.stringify(data[list[key]]['value'])
				for (var i=0; i<list.length; i++) {
					if (data[list[i]]['type'] == 'hidden') {
						//var value = JSON.stringify(data[list[key]]['value']);
						var value = data[list[i]]['value'];
						$('#' + formId).append("<input type=\"hidden\" id=\"id_" + formId + '_' + list[i] + "\" name=\"" + list[i] + "\"  />");
						$("#id_" + formId + '_' + list[i]).attr('value', value);
						// Inject viewNameSource : viewName is same as formId
						if (list[i] == 'viewNameSource') {
							$("#id_" + formId + '_' + list[i]).attr('value', viewName);
						}
					}				
				}				
			}
			//ximpia.console.log($('#' + formId));
		}
        };
		
        if ( methods[method] ) {
            return methods[ method ].apply( this, Array.prototype.slice.call( arguments, 1 ));
        } else if ( typeof method === 'object' || ! method ) {
            return methods.init.apply( this, arguments );
        } else {
            $.error( 'Method ' +  method + ' does not exist on jQuery.xpHidden' );
        }    
		
	};

})(jQuery);

/*
 * 
 *
 * Ximpia Visual Component Check: Checkbox button with fields coming from choices (choices class or foreign key)
 *  
 * ** HTML **
 * 
 * <div id="id_mycheck_comp" data-xp-type="check" data-xp="{alignment: 'vertical'}" > </div>
 * 
 * 
 * Your form should have ``mycheck``field
 * 
 * ** Attributes (data-xp) **
 * 
 * * ``alignment`` [optional] : 'vertical', 'horizontal'
 * * ``hasLabel`` [optional] : "true"|"false". Weather to show or not a label, at left or top of radio controls.
 * * ``label`` [optional] : Field label
 * * ``labelPosition`` [optional] : 'top'|'left'. Label position, left of radio buttons, or top for label at one line and radio
 * 									controls on a new line.
 * * ``controlPosition`` [optional] : 'before'|'after'. Default: 'before'. Position for the radio control, after or before text.
 * * ``info``[optional] : Displays tooltip with helpText field data.
 * 
 * Having alignment vertical will show ``ui-option-vertical`` class. Alignment horizontal has class ``ui-option-horizontal``
 * 
 * 
 * ** Interfaces **
 * 
 * This components implements these interfaces:
 * 
 * * ``IInputList``
 *  
 * 
 * ** Methods **
 * 
 * * ``render``
 * * ``disable``
 * * ``enable``
 * 
 * 
 *
 */

(function($) {	

	$.fn.xpCheck = function( method ) {  

        // Settings		
        var settings = {
        	labelPosition: 'left',
        	controlPosition: 'before',
        	reRender: false
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
		render: function(xpForm) {
			/**
			 * Render for radio buttons
			 */
			// id_month_comp : choiceId:'months'
			ximpia.console.log('xpOption :: option ... render...');
			var data = ximpia.common.Browser.getFormDataFromSession(xpForm);
			ximpia.console.log(data);
			for (var i=0; i<$(this).length; i++) {
				var element = $(this)[i];
				ximpia.console.log('xpOption :: element : ' + element); 
				var idBase = $(element).attr('id').split('_comp')[0];
				var name = idBase.split('id_')[1];
				ximpia.console.log('xpOption :: idBase : ' + idBase);
				var hasToRender = ximpia.common.Form.hasToRender(element, settings.reRender);
				if (hasToRender == true && data.hasOwnProperty(name)) {					
					var value = "";
					var choicesId = "";
					value = data[name]['value'];
					choicesId = data[name]['choicesId']
					$.metadata.setType("attr", "data-xp");
					var attrs = $(element).metadata();
	        		// Choices
	        		ximpia.console.log('xpOption :: choicesId: ' + choicesId);
	        		var choiceList = JSON.parse(data['choices']['value'])[choicesId];
	        		ximpia.console.log('xpOption :: choicesList: ' + choiceList);
	        		var htmlContent = "";
	        		if (!attrs.hasOwnProperty('labelPosition') && attrs.hasOwnProperty('hasLabel')) {
	        			attrs['labelPosition'] = settings.labelPosition;
	        		}
	        		if (!attrs.hasOwnProperty('controlPosition')) {
	        			attrs['controlPosition'] = settings.controlPosition;
	        		}
	        		if (attrs['alignment'] == 'vertical' && attrs.hasOwnProperty('hasLabel') && attrs['hasLabel'] == true) {	        			
	        			attrs['labelPosition'] = 'top';
	        		}
	        		// Label:
	        		var label = data[name]['label'];
	        		if (attrs.hasOwnProperty('label')) {
	        			label = attrs['label'];
	        		}
	        		var classLabel = 'ui-check-label-left';
	        		if (attrs.hasOwnProperty('hasLabel') && attrs.hasOwnProperty('labelPosition') && attrs['labelPosition'] == 'top') {
	        			classLabel = 'ui-check-label-top';
	        		}
	        		if (attrs.hasOwnProperty('hasLabel') && attrs['hasLabel']) {
	        			htmlContent += "<div class=\"" + classLabel + "\" >";
	        			var helpText = "";
	        			if (attrs.hasOwnProperty('info') && attrs.info == true && data[name].hasOwnProperty('helpText')) {
	        				helpText = "data-xp-title=\"" + data[name]['helpText'] + "\""
	        			}
	        			var attrClass = "";
	        			if (attrs.hasOwnProperty('info') && attrs.info == true) {
	        				attrClass = "class=\"info\"";
	        			}
	        			htmlContent += "<label for=\"id_" + name + "_" + choiceList[0][0] + "\" " + attrClass+ " " + helpText + 
	        					" style=\"margin-right: 5px\">" + label + "</label>";
	        			if (attrs.labelPosition == 'left') {
	        				htmlContent += ': ';
	        			}
	        			htmlContent += "</div>";	        			
	        		}
	        		// Option items
	        		if (attrs.alignment == 'horizontal') {
	        			htmlContent += "<ul class=\"ui-check-horizontal\">";
	        		} else  {
	        			htmlContent += "<ul class=\"ui-check-vertical\">";
	        		}
					for (var j=0 ; j<choiceList.length; j++) {
						htmlContent += "<li>";
						var controlHtml = "";
						var ctlId = "id_" + name + "_" + choiceList[j][0];
						if (choiceList[j][0] == value) {
							controlHtml += "<input id=\"" + ctlId + "\" type=\"checkbox\" data-xp-type=\"check\" name=\"" + name + 
								"\" value=\"" + choiceList[j][0] + "\" data-xp=\"{}\" checked=\"checked\"";
						} else {
							controlHtml += "<input id=\"" + ctlId + "\" type=\"checkbox\" data-xp-type=\"check\" name=\"" + name + 
								"\" value=\"" + choiceList[j][0] + "\" data-xp=\"{}\"";
						}
						controlHtml += "/>";
						if (attrs['controlPosition'] == 'before') {
							htmlContent += controlHtml + "<label for=\"" + ctlId + "\">" + choiceList[j][1] + "</label>";
						} else {
							htmlContent += "<label for=\"" + ctlId + "\">" + choiceList[j][1] + "</label>" + controlHtml;
						}
						htmlContent += "</li>";
					}
					htmlContent += "</ul>";
					// Assign html visual component div element
					$(element).html(htmlContent);
					// Help text...
					// Set render, since we have rendered visual component
					$(element).attr('data-xp-render', JSON.stringify(true));
					// Trace
					ximpia.console.log(htmlContent);
				} else if (!data.hasOwnProperty(name)) {
					ximpia.console.log('xpOption.render :: server data has no variable');
				}
			}
		},
		disable: function() {
			for (var i=0; i<$(this).length; i++) {
				// Get all option items and disable them
				$(this).find("input[data-xp-type='check']").each(function() {
					$(this).attr('disabled', true);
				})				
			}
		},
		enable: function() {
			for (var i=0; i<$(this).length; i++) {
				// Get all option items and disable them
				$(this).find("input[data-xp-type='check']").each(function() {
					$(this).attr('disabled', false);
				})				
			}
		},
		unrender: function() {
			for (var i=0; i<$(this).length; i++) {
				$(this).empty();
				$(this).removeAttr('data-xp-render');
			}
		}
        };		
        if ( methods[method] ) {
            return methods[ method ].apply( this, Array.prototype.slice.call( arguments, 1 ));
        } else if ( typeof method === 'object' || ! method ) {
            return methods.init.apply( this, arguments );
        } else {
            $.error( 'Method ' +  method + ' does not exist on jQuery.xpCheck' );
        }
	};

})(jQuery);

/*
 * List of fields. Fields can be added, deleted. Will represent the many-to-many relationships in models
 * 
 * TODO: Include the html for component
 *
 */

(function($) {	

	$.fn.xpFieldList = function( method ) {  

        // Settings		
        var settings = {
        	excudeListSelect: ['type','id','element','help_text','label','data-xp-val', 'value', 'choices','choicesId'],
        	excludeListLabel: ['type','id','element'],
        	excludeList: ['info','type']
        };
        
        var addField = function(inputField, feedType, choicesId) {
        	ximpia.console.log('addField...');
        	ximpia.console.log('inputField: ' + inputField + ' feedType: ' + feedType);
        	var inputDataId = inputField.split('_comp')[0];
        	if (feedType == 'input') {
        		var idBase = inputField.split('Input_comp')[0];
			var data = $("#" + inputDataId).prop('value');
			var dataId = data
        	} else if (feedType == 'select') {
        		var idBase = inputField.split('Select_comp')[0];
        		var dataId = $("#" + inputDataId).prop('value');
        		// Get from choices data
        		var choiceList = JSON.parse($('#id_choices').attr('value'))[choicesId];
        		for (j in choiceList) {
        			if (choiceList[j][0] == dataId) {
        				data = choiceList[j][1];
        			}
        		}
        	}				
		ximpia.console.log('data: ' + data + ' dataId: ' + dataId)	
		var idBaseList = idBase + 'ListValue';
		ximpia.console.log('idBaseList: ' + idBaseList);
		var obj = new ximpia.visual.GenericComponentData();
		obj.init(idBaseList);
		var hasElement = obj.hasElement(dataId);
		var size = obj.getSize();
		var idTag = idBase + '_' + size;
		var idTagClick = idBase + '_click_' + size;
		var idTagDel = idBase + '_del_' + size;
		validate = false;
		if (dataId != '' && size < settings.limit && hasElement == false) {
			validate = true;
		}
		ximpia.console.log('validate: ' + validate);				
		if (validate == true) {
			var sHtml = '<div id="' + idTag + '" class="listField"><div id="' + idTagClick + '" class="listFieldText">' + data + '</div><div class="listFieldSep">&nbsp;</div><div id="' + idTagDel + '" class="listFieldDel">X</div></div>';
			ximpia.console.log(sHtml);
			$('#' + idBase + 'Show').append(sHtml);
			var tagObj = new Object();
			tagObj.id = size;
			tagObj.text = dataId;
			obj.addDataEnd(tagObj);
			if (feedType == 'input') {
				$('#' + inputDataId).prop('value', '');
				$('#' + inputDataId).focus();
			} else if (feedType == 'select') {
				$('#' + idBase + 'Select_input').prop('value', '');
			}

			// Remove Field Bind
			$('#' + idTagDel).click(function() {
				var idElementDel = $(this).attr('id');
        			var idElement = idElementDel.replace('_del','');
        			var list = idElement.split('_');
				var index = list[list.length-1];
        			$('#' + idElement).remove();
        			obj.deleteData(index);
        			// Logic when field is deleted
        			// TODO: Define how to call to logic, n function with arguments, etc....
        			/*if (oArg.callBack) {
	        			oArg.callBack(oArg);
        			}*/
				$('#' + inputDataId).focus();
			});
		} else if (size >= settings.limit) {
			// TODO: Show a fancy messahe window
			alert('Can´t include more fields to the list');
		}
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
		render: function() {	
			var data = JSON.parse(sessionStorage.getItem("xpForm"));
			//var container = $("#id_groupTags").xpContainer({limit: 10, 
									//doKey: true, 
									//args: {idText: 'id_organizationGroupTags', button: 'BtAddTag'}});
			//container.xpContainer('addTag');			
			
			/*
			 * {	limit: 10, 
			 * 	doKey: true, 
			 * 	args: {
			 * 		idText: 'id_organizationGroupTags', 
			 * 		button: 'BtAddTag'
			 * 		}
			 * 	}
			 */
			
			ximpia.console.log('render fields...');
			//ximpia.console.log($(this));
			for (var i=0; i<$(this).length; i++) {
				//ximpia.console.log($(this)[i]);
				var element = $(this)[i];
				ximpia.console.log('element : ' + element); 
				var idBase = $(element).attr('id').split('_comp')[0];
				ximpia.console.log('idBase : ' + idBase);
				var doRender = ximpia.common.Form.doRender(element, settings.reRender);
				if (doRender == true) {
					var name = idBase.split('id_')[1];
					var nameInput = name + 'Input';
					var nameSelect = name + 'Select';
					var nameList = name + 'ListValue';
					$.metadata.setType("attr", "data-xp");
					var attrs = $(element).metadata();
					var dataInputAttrs = data[nameInput];
					var dataSelectAttrs = data[nameSelect];
					var dataListAttrs = data[nameList];
					ximpia.console.log('attrs....');
					ximpia.console.log(attrs);
					ximpia.console.log('dataInputAttrs....');
					ximpia.console.log(dataInputAttrs);
					ximpia.console.log('dataInputAttrs....');
					ximpia.console.log(dataSelectAttrs);
					ximpia.console.log('dataSelectAttrs....');
					ximpia.console.log(dataListAttrs);
					/*var type = 'text';
					if (attrs.hasOwnProperty('type')) {
						type = attrs.type;
					}*/
					// id, name, type
					var inType = attrs.inType;
					if (inType == "input") {
						var htmlContent = "";
						htmlContent = htmlContent + "<div id=\"" + idBase + 'Input_comp' + "\" data-xp-type=\"text.autocomplete\" data-xp=\"{info: true, left: 145}\" style=\"float: left\" data-xp-related=\"list.field\" ></div>";
						htmlContent = htmlContent + "<div style=\"float: left\"><a href=\"#\" class=\"buttonIcon buttonIconSmall\" onclick=\"return false;\" data-xp-type=\"button.field\" data-xp=\"{input: " + idBase + "Input_comp, type: 'input'}\" >Add</a></div>";
						htmlContent = htmlContent + "<div id=\"" + idBase + "Show\" class=\"listContainer\" style=\"width: 300px; margin-left: 15px; margin-top: 4px\" ></div><div style='clear:both'></div>";
						htmlContent = htmlContent + "<input type=\"hidden\" name=\"" + nameList + "\" id=\"" + idBase + "ListValue\" value=\"\" />";
					} else if (inType == "select") {
						var htmlContent = "";
						htmlContent = htmlContent + "<div id=\"" + idBase + 'Select_comp' + "\" data-xp-type=\"list.select\" data-xp=\"{left: 85, info: true}\" style=\"float: left\" data-xp-related=\"list.field\" ></div>";
						htmlContent = htmlContent + "<div style=\"float: left\"><a href=\"#\" class=\"buttonIcon buttonIconSmall\" onclick=\"return false;\" data-xp-type=\"button.field\" data-xp=\"{input: " + idBase + "Select_comp, type: 'select', choicesId: '" + dataSelectAttrs.choicesId + "'}\" >Add</a></div>";
						htmlContent = htmlContent + "<div id=\"" + idBase + "Show\" class=\"listContainer\" style=\"width: 300px; margin-left: 15px; margin-top: 4px\" ></div><div style='clear:both'></div>";
						htmlContent = htmlContent + "<input type=\"hidden\" name=\"" + nameList + "\" id=\"" + idBase + "ListValue\" value=\"\" />";
					}
					$(element).html(htmlContent);
					$(element).attr('data-xp-render', JSON.stringify(true));
					$(element).css('clear', 'both');
					ximpia.console.log('field list html...');
					ximpia.console.log(htmlContent);
				}				
			}			
			// Bind click event to add button
			$("[data-xp-type='button.field']").click(function() {
				var attrsButton = $(this).metadata();
				var inputField = attrsButton['input'].id;
				ximpia.console.log('inputField: ' + inputField);
				var feedType = attrsButton['type'];
				ximpia.console.log('feedType: ' + feedType);
				var choicesId = "";
				if (attrsButton.hasOwnProperty('choicesId')) {
					choicesId = attrsButton['choicesId'];
					ximpia.console.log('choicesId: ' + choicesId);
				}
				addField(inputField, feedType, choicesId);
			});
		},
		bindKeyPress: function() {
			for (var i=0; i<$(this).length; i++) {
				var element = $(this)[i];
				$(element).keypress(function(e) {
					if (e.which == 13) {
						var inputField = e.currentTarget.id + '_comp';
						ximpia.console.log('inputField: ' + inputField);
                				addField(inputField, 'input');
					}
				});
			}			
		}
        };
		
        if ( methods[method] ) {
            return methods[ method ].apply( this, Array.prototype.slice.call( arguments, 1 ));
        } else if ( typeof method === 'object' || ! method ) {
            return methods.init.apply( this, arguments );
        } else {
            $.error( 'Method ' +  method + ' does not exist on jQuery.xpListField' );
        }    
		
	};

})(jQuery);

/*
 * 
 *
 * Ximpia Visual Component Option: Radio button with fields coming from choices
 *  
 * ** HTML **
 * 
 * <div id="id_myoption_comp" data-xp-type="option" data-xp="{type: 'radio', alignment: 'vertical'}" > </div>
 * 
 * <div id="id_myoption_comp" data-xp-type="option" data-xp="{type: 'check', alignment: 'vertical'}" > </div>
 * 
 * Your form should have ``myoption``field
 * 
 * ** Attributes (data-xp) **
 * 
 * * ``type`` : 'radio', 'check'
 * * ``alignment`` [optional] : 'vertical', 'horizontal'
 * * ``hasLabel`` [optional] : "true"|"false". Weather to show or not a label, at left or top of radio controls.
 * * ``label`` [optional] : Field label
 * * ``labelPosition`` [optional] : 'top'|'left'. Label position, left of radio buttons, or top for label at one line and radio
 * 									controls on a new line.
 * * ``controlPosition`` [optional] : 'before'|'after'. Default: 'before'. Position for the radio control, after or before text.
 * * ``info``[optional] : Displays tooltip with helpText field data.
 * 
 * Having alignment vertical will show ``ui-option-vertical`` class. Alignment horizontal has class ``ui-option-horizontal``
 * 
 * 
 * ** Interfaces **
 * 
 * This components implements these interfaces:
 * 
 * * ``IInputList``
 *  
 * 
 * ** Methods **
 * 
 * * ``render``
 * * ``disable``
 * * ``enable``
 * 
 * ** Types **
 * * ``radio``: radio option box
 * * ``checkbox``: check box. Behaved like option, when user clicks on one, it gets selected. Ability to have no option cheched.
 * 
 *
 */


(function($) {	

	$.fn.xpOption = function( method ) {  

        // Settings		
        var settings = {
        	labelPosition: 'left',
        	controlPosition: 'before',
        	reRender: false
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
		render: function(xpForm) {
			/**
			 * Render for radio buttons
			 */
			// id_month_comp : choiceId:'months'
			ximpia.console.log('xpOption :: option ... render...');
			var data = ximpia.common.Browser.getFormDataFromSession(xpForm);
			ximpia.console.log(data);
			for (var i=0; i<$(this).length; i++) {
				var element = $(this)[i];
				ximpia.console.log('xpOption :: element : ' + element); 
				var idBase = $(element).attr('id').split('_comp')[0];
				var name = idBase.split('id_')[1];
				ximpia.console.log('xpOption :: idBase : ' + idBase);
				var hasToRender = ximpia.common.Form.hasToRender(element, settings.reRender);
				if (hasToRender == true && data.hasOwnProperty(name)) {					
					var value = "";
					var choicesId = "";
					value = data[name]['value'];
					choicesId = data[name]['choicesId']
					$.metadata.setType("attr", "data-xp");
					var attrs = $(element).metadata();
	        		// Choices
	        		ximpia.console.log('xpOption :: choicesId: ' + choicesId);
	        		var choiceList = JSON.parse(data['choices']['value'])[choicesId];
	        		ximpia.console.log('xpOption :: choicesList: ' + choiceList);
	        		var htmlContent = "";
	        		if (!attrs.hasOwnProperty('labelPosition') && attrs.hasOwnProperty('hasLabel')) {
	        			attrs['labelPosition'] = settings.labelPosition;
	        		}
	        		if (!attrs.hasOwnProperty('controlPosition')) {
	        			attrs['controlPosition'] = settings.controlPosition;
	        		}
	        		if (attrs['alignment'] == 'vertical' && attrs.hasOwnProperty('hasLabel') && attrs['hasLabel'] == true) {	        			
	        			attrs['labelPosition'] = 'top';
	        		}
	        		// Label:
	        		var label = data[name]['label'];
	        		if (attrs.hasOwnProperty('label')) {
	        			label = attrs['label'];
	        		}
	        		var classLabel = 'ui-option-label-left';
	        		if (attrs.hasOwnProperty('hasLabel') && attrs.hasOwnProperty('labelPosition') && attrs['labelPosition'] == 'top') {
	        			classLabel = 'ui-option-label-top';
	        		}
	        		if (attrs.hasOwnProperty('hasLabel') && attrs['hasLabel']) {
	        			htmlContent += "<div class=\"" + classLabel + "\" >";
	        			var helpText = "";
	        			if (attrs.hasOwnProperty('info') && attrs.info == true && data[name].hasOwnProperty('helpText')) {
	        				helpText = "data-xp-title=\"" + data[name]['helpText'] + "\""
	        			}
	        			var attrClass = "";
	        			if (attrs.hasOwnProperty('info') && attrs.info == true) {
	        				attrClass = "class=\"info\"";
	        			}
	        			htmlContent += "<label for=\"id_" + name + "_" + choiceList[0][0] + "\" " + attrClass+ " " + helpText + 
	        					" style=\"margin-right: 5px\">" + label + "</label>";
	        			if (attrs.labelPosition == 'left') {
	        				htmlContent += ': ';
	        			}
	        			htmlContent += "</div>";	        			
	        		}
	        		// Option items
	        		if (attrs.alignment == 'horizontal') {
	        			htmlContent += "<ul class=\"ui-option-horizontal\">";
	        		} else  {
	        			htmlContent += "<ul class=\"ui-option-vertical\">";
	        		}
					for (var j=0 ; j<choiceList.length; j++) {
						htmlContent += "<li>";
						var controlHtml = "";
						var ctlId = "id_" + name + "_" + choiceList[j][0];
						if (choiceList[j][0] == value) {
							if (attrs.type == 'radio') {
								controlHtml += "<input id=\"" + ctlId + "\" type=\"radio\" data-xp-type=\"option\" name=\"" + name + 
									"\" value=\"" + choiceList[j][0] + "\" data-xp=\"{}\" checked=\"checked\"";
							} else {
								controlHtml += "<input id=\"" + ctlId + "\" type=\"checkbox\" data-xp-type=\"option\" name=\"" + name + 
									"\" value=\"" + choiceList[j][0] + "\" data-xp=\"{}\" checked=\"checked\"";
							}
						} else if (attrs.type == 'radio' && j == 0 && choiceList[j][0] != value) {
							controlHtml += "<input id=\"" + ctlId + "\" type=\"radio\" data-xp-type=\"option\" name=\"" + name + 
									"\" value=\"" + choiceList[j][0] + "\" data-xp=\"{}\" checked=\"checked\"";
						} else {
							if (attrs.type == 'radio') {
								controlHtml += "<input id=\"" + ctlId + "\" type=\"radio\" data-xp-type=\"option\" name=\"" + name + 
									"\" value=\"" + choiceList[j][0] + "\" data-xp=\"{}\"";
							} else {
								controlHtml += "<input id=\"" + ctlId + "\" type=\"checkbox\" data-xp-type=\"option\" name=\"" + name + 
									"\" value=\"" + choiceList[j][0] + "\" data-xp=\"{}\"";
							}
						}
						controlHtml += "/>";
						if (attrs['controlPosition'] == 'before') {
							htmlContent += controlHtml + "<label for=\"" + ctlId + "\">" + choiceList[j][1] + "</label>";
						} else {
							htmlContent += "<label for=\"" + ctlId + "\">" + choiceList[j][1] + "</label>" + controlHtml;
						}
						htmlContent += "</li>";
					}
					htmlContent += "</ul>";
					// Assign html visual component div element
					$(element).html(htmlContent);
					// Help text...
					// Set render, since we have rendered visual component
					$(element).attr('data-xp-render', JSON.stringify(true));
					// Trace
					ximpia.console.log(htmlContent);
				} else if (!data.hasOwnProperty(name)) {
					ximpia.console.log('xpOption.render :: server data has no variable');
				}
			}
			// Click option items
			$("input[type='checkbox'][data-xp-type='option']").click(function(evt, unchecked) {
				if ($(this)[0].checked == true && typeof(unchecked) == 'undefined') {
					// New click from user
					//ximpia.console.log('xpOption.render :: checked: ' + $(this)[0].checked);
					var name = $(this).attr('name');
					var checkedItems = $("input[name='" + name + "']:checked");
					//ximpia.console.log(checkedItems);
					// Uncheck item
					if (checkedItems.length > 0) {
						for (var i=0; i<checkedItems.length; i++) {
							if (checkedItems[i].id != $(this).attr('id')) {
								//ximpia.console.log('xpOption.render :: Will click on ' + checkedItems[i].id);
								// We set uncheck to true, so that will not try to check values
								$("#" + checkedItems[i].id).trigger('click', [true]);
							}							
						}
					}				
				}
			})
		},
		disable: function() {
			for (var i=0; i<$(this).length; i++) {
				// Get all option items and disable them
				$(this).find("input[data-xp-type='option']").each(function() {
					$(this).attr('disabled', true);
				})				
			}
		},
		enable: function() {
			for (var i=0; i<$(this).length; i++) {
				// Get all option items and disable them
				$(this).find("input[data-xp-type='option']").each(function() {
					$(this).attr('disabled', false);
				})				
			}
		},
		unrender: function() {
			for (var i=0; i<$(this).length; i++) {
				$(this).empty();
				$(this).removeAttr('data-xp-render');
			}
		}
        };		
        if ( methods[method] ) {
            return methods[ method ].apply( this, Array.prototype.slice.call( arguments, 1 ));
        } else if ( typeof method === 'object' || ! method ) {
            return methods.init.apply( this, arguments );
        } else {
            $.error( 'Method ' +  method + ' does not exist on jQuery.xpOption' );
        }
	};

})(jQuery);

/*
 * Ximpia Visual Component Input: Text, Password, etc...
 * 
 * TODO: Include the html for component
 *
 */

(function($) {	

	$.fn.xpListSelect = function( method ) {  

        // Settings		
        var settings = {
        	excudeListSelect: ['type','id','element','help_text','label','data-xp-val', 'value', 'choices','choicesId'],
        	excludeListLabel: ['type','id','element'],
        	excludeList: ['info','type','left'],
        	htmlAttrs: ['tabindex','readonly','maxlength','class','value','name','autocomplete'],
        	djangoAttrs: ['type','id','info','help_text','label','element','left','xptype','choices'],
        	formData: {}
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
		render: function(xpForm) {
			var data = ximpia.common.Browser.getFormDataFromSession(xpForm);
			var myForm = ximpia.common.Form.getForm(xpForm);
			//var data = JSON.parse(sessionStorage.getItem("xpForm"));
			console.log($(this));
			console.log('Elements : ' + $(this).length);
			for (var i=0; i<$(this).length; i++) {
				console.log($(this)[i]);
				var element = $(this)[i];
				var doRender = ximpia.common.Form.doRender(element, settings.reRender);
				if (doRender == true) {				 
					var idInputSrc = $(element).attr('id').split('_comp')[0];
					var idInput = $(element).attr('id').split('_comp')[0] + '_input';
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
						htmlContent = "<div style=\"float: left; border: 0px solid\"><label for=\"" + idInput + "\"></label>:</div> <div id=\"" + idField + "\" style=\"float: left; margin-top: 2px; margin-left: 3px\" ></div>";
					}
					console.log(htmlContent);
					$(element).html(htmlContent);
					$(element).attr('data-xp-render', JSON.stringify(true));
					// Plugin
					//var countryList = JSON.parse(JSON.parse($('#id_' + myForm + '_choices').attr('value')))[choicesId];
					var countryList = JSON.parse($('#id_' + myForm + '_choices').attr('value'))[choicesId];
					var results = {'results': []};
					for (j in countryList) {
						results['results'][j] = {'id': countryList[j][0], 'name': countryList[j][1]}
					}
					console.log('idField : ' + idField);
					// *************
					// ** Flexbox **
					// *************
					// input: maxVisibleRows, allowInput
					var fb = $("#" + idField).flexbox(results,{
						autoCompleteFirstMatch: true,
						paging: false,
						maxVisibleRows: 10
					});
					//fb.setValue('es', 'Spain');
					// Input
					ximpia.common.Form.doAttributes({
						djangoAttrs: settings.djangoAttrs,
						htmlAttrs: settings.htmlAttrs,
						excludeList: settings.excludeList,
						dataAttrs: dataAttrs,
						attrs: attrs,
						idElement: idInput,
						skipName: true
					});					
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
				}
			}
		},
		disable: function() {
			var idField = $(this).attr('id').split('_comp')[0] + '_field';
			var id = '#' + idField.split('_field')[0];
			$(id + '_input').attr('disabled', 'disabled');
			$('#' + idField + '_arrow').unbind('mouseenter mouseleave click mousedown mouseup');
		},
		setValue: function(xpForm, code) {
			var formId = ximpia.common.Browser.getForm(xpForm);
			ximpia.console.log('setValue :: formId: ' + formId);
			ximpia.console.log('setValue :: xpForm: ' + xpForm);
			var data = ximpia.common.Browser.getFormDataFromSession(xpForm);			
			var idField = $(this).attr('id').split('_comp')[0] + '_field';
        		var id = '#' + idField.split('_field')[0];
        		var nameField = idField.split('_field')[0].split('id_')[1];
        		ximpia.console.log('setValue :: nameField: ' + nameField);
        		ximpia.console.log(data);
        		var field = data[nameField];
        		var choicesId = field['choicesId'];
        		ximpia.console.log('setValue :: choicesId: ' + choicesId);
        		var countryList = ximpia.common.Choices.get(formId, choicesId);
        		ximpia.console.log('setValue :: countryList: ' + countryList);
			var value = ximpia.common.List.getValueFromList(code, countryList);
        		$(id).val(code).removeClass('watermark');
        		$(id + '_input').val(value).removeClass('watermark');			
		}	
        };
		
        if ( methods[method] ) {
            return methods[ method ].apply( this, Array.prototype.slice.call( arguments, 1 ));
        } else if ( typeof method === 'object' || ! method ) {
            return methods.init.apply( this, arguments );
        } else {
            $.error( 'Method ' +  method + ' does not exist on jQuery.xpListSelect' );
        }    
		
	};

})(jQuery);

/*
 * Ximpia Visual Component Input: Text, Password, etc...
 *
 */

(function($) {	

	$.fn.xpSelect = function( method ) {  

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
			for (var i=0; i<$(this).length; i++) {
				//console.log($(this)[i]);
				var element = $(this)[i]; 
				var idInput = $(element).attr('id').split('_comp')[0];
				var doRender = ximpia.common.Form.doRender(element, settings.reRender);
				if (doRender == true) {
					var nameInput = idInput.split('id_')[1];
					$.metadata.setType("attr", "data-xp");
					var attrs = $(element).metadata();
					var dataAttrs = data[nameInput];
					//console.log(dataAttrs);
					var type = 'text';
					var value = "";
					if (attrs.hasOwnProperty('type')) {
						type = attrs.type;
					}
					// id, name, type
					var htmlContent = "";
					if (attrs.hasOwnProperty('left')) {
						htmlContent = "<div style=\"width: " + attrs['left'] + "px; float: left; border: 0px solid\"><label for=\"" + idInput + "\"></label>:</div> <div style=\"border: 0px solid; float: left\"><select id=\"" + idInput + "\" data-xp-class=\"combobox\"  ></select></div>";
					} else {
						htmlContent = "<div style=\"float: left; border: 0px solid\"><label for=\"" + idInput + "\"></label>:</div> <div style=\"border: 0px solid; float: left; margin-left: 5px \"><select id=\"" + idInput + "\" data-xp-class=\"combobox\" ></select></div>";
					}
					$(element).html(htmlContent);
					$(element).attr('data-xp-render', JSON.stringify(true));				
					// Input
					for (attr in dataAttrs) {
						var exists = ximpia.common.ArrayUtil.hasKey(settings.excudeListSelect, attr);
						if (exists == false) {
							value = dataAttrs[attr];
							/*if (attr == 'class') {
								value = value + ' scroll';
							}
							console.log(attr + ' - ' + value);*/
							$("#" + idInput).attr(attr, value);
						}					
					}
					for (attr in attrs) {
						var exists = ximpia.common.ArrayUtil.hasKey(settings.excludeList, attr);
						if (exists == false) {
							value = attrs[attr];
							/*if (attr == 'class') {
								value = value + 'scroll';
							}*/
							$("#" + idInput).attr(attr, value);
						}					
					}				
					// Choices
					var choicesId = dataAttrs['choicesId'];
					var choices = JSON.parse($("#id_choices").attr('value'))[choicesId];
					/*console.log('choices...');
					console.log('choicesId : ' + choicesId);
					console.log(choices)*/
					for (choiceIndex in choices) {
						var htmlSelect = "<option value=\"" + choices[choiceIndex][0] + "\">" + choices[choiceIndex][1] + "</option>";
						$("#" + idInput).append(htmlSelect);
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
				}				
			}
		},
		disable: function() {
			var idInput = $(this).attr('id').split('_comp')[0];
			$("#" + idInput).attr('disable', 'disable');
		},
		enable: function() {
		}	
        };
		
        if ( methods[method] ) {
            return methods[ method ].apply( this, Array.prototype.slice.call( arguments, 1 ));
        } else if ( typeof method === 'object' || ! method ) {
            return methods.init.apply( this, arguments );
        } else {
            $.error( 'Method ' +  method + ' does not exist on jQuery.xpInput' );
        }    
		
	};

})(jQuery);

/*
 * Ximpia Visual Component TextArea
 * 
 * TODO: Include the html for component
 *
 */

(function($) {	

	$.fn.xpTextArea = function( method ) {  

        // Settings		
        var settings = {
        	excudeListInput: ['type','id','element','help_text','label','left'],
        	excudeListInputSug: ['type','id','element','help_text','label','left'],
        	excludeListLabel: ['type','id','element'],
        	excludeList: ['info','type','left'],
		'maxLimit' : 144,
		'maxHeight' : 150
        };
                
        var setCSS = function(which){
        	// Init the div for the current textarea
        	var id = which.attr('id') + '_hidden';
        	$("#" + id).css({
        		'position':'absolute',
        		'top': -10000,
        		'left': -10000,
        		'width': $(which).width()-20,
        		'min-height': $(which).height(),
        		'font-family': $(which).css('font-family'),
        		'font-size': $(which).css('font-size'),
        		'line-height': $(which).css('line-height')
        	});
        	if($.browser.msie && parseFloat($.browser.version) < 7){
        		$("#" + id).css('height',$(which).height());
        	};
        };                
        var copyContent = function(which){
        	// Convert the line feeds into BRs
        	var id = which.attr('id') + '_hidden';
        	theValue = $(which).val() || "";
        	theValue = theValue.replace(/\n/g,'<br />');
        	$("#" + id).html(theValue + '<br />');
        	$(which).height($("#" + id).height());						
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
		render: function(xpForm) {
			console.log('textarea render....');
			var data = ximpia.common.Browser.getFormDataFromSession(xpForm);
			//var data = JSON.parse(sessionStorage.getItem("xpForm"));
			console.log($(this));
			console.log('Elements : ' + $(this).length);
			for (var i=0; i<$(this).length; i++) {
				console.log($(this)[i]);
				var element = $(this)[i];
				var idInput = $(element).attr('id').split('_comp')[0];
				var nameInput = idInput.split('id_')[1];
				var doRender = ximpia.common.Form.doRender(element, settings.reRender);
				if (doRender == true) {
					$.metadata.setType("attr", "data-xp"); 
					var attrs = $(element).metadata();
					var dataAttrs = data[nameInput];
					console.log('idInput: ' + idInput);
					console.log('nameInput: ' + nameInput)
					console.log('*** text area data : dataAttrs ***');
					console.log(dataAttrs);
					console.log('*** text area data : attrs ***');
					console.log(attrs);
					var htmlContent = "";
					htmlContent += "<div><label for=\"" + idInput + "\"></label>: ";
					htmlContent += "<textarea id=\"" + idInput + "\"/> </div>";
					//htmlContent += "<td valign=\"bottom\" style=\"width: 30px\"><span id=\"\" class=\"textAreaCounter\" style=\" font-size:90%; position:relative; top: 7px\"></span></td></tr></table>";
					$(element).html(htmlContent);
					$(element).attr('data-xp-render', JSON.stringify(true));
					// Input
					for (attr in dataAttrs) {
						var exists = ximpia.common.ArrayUtil.hasKey(settings.excudeListInput, attr);
						if (exists == false) {
							$("#" + idInput).attr(attr, dataAttrs[attr]);
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
					var textarea = $("#" + idInput);
        				var id = textarea.attr('id') + '_hidden';
        				$('body').append('<div id="' + id + '"></div>');
					console.log('textarea...');
					console.log(textarea);      			
        				textarea.css({
	            				'overflow':'hidden'
        				})
        				.bind('keyup',function(){
        					//console.log('writing...');
						var size = textarea.val().length;
                				if (size < settings.maxLimit) {
	                    				copyContent(textarea);
							if (textarea.hasClass('error')) {
								textarea.removeClass('error');
								textarea.addClass('valid');
							}
                				} else {
		                    			copyContent(textarea);
							textarea.addClass('error');
							if (textarea.hasClass('valid')) {
								textarea.removeClass('valid');
							}
                				}
					//}
        				});
        				// Make sure all the content in the textarea is visible
        				setCSS(textarea);
        				copyContent(textarea);
					textarea.height($("#" + id).height());		
				//};			
				}	
			}
		},
		disable: function() {
		}
        };
		
        if ( methods[method] ) {
            return methods[ method ].apply( this, Array.prototype.slice.call( arguments, 1 ));
        } else if ( typeof method === 'object' || ! method ) {
            return methods.init.apply( this, arguments );
        } else {
            $.error( 'Method ' +  method + ' does not exist on jQuery.xpInput' );
        }    		
	};
})(jQuery);
