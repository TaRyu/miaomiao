/**
 * @license Copyright (c) 2003-2015, CKSource - Frederico Knabben. All rights reserved.
 * For licensing, see LICENSE.md or http://ckeditor.com/license
 */

CKEDITOR.editorConfig = function( config ) {
	// Define changes to default configuration here. For example:
    // config.extraPlugins = 'codesnippet';
	config.language = 'zh-cn';
    config.font_names='宋体/宋体;黑体/黑体;仿宋/仿宋_GB2312;楷体/楷体_GB2312;隶书/隶书;幼圆/幼圆;微软雅黑/微软雅黑;'+ config.font_names;
	// config.uiColor = '#AADC6E';
    // config.font_defaultLabel = '黑体';
    config.font_style = {
        element:        'span',
        styles:         { 'font-family': '宋体' },
        overrides:      [ { element: 'font', attributes: { 'face': null } } ]
    };
};
