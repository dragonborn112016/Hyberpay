/**
 * Created by chitra on 12/10/15.
 */
(function () {
    'use strict';

    var app = angular.module('app', [
        // Angular modules

        'ngRoute',  // routing
        'ngAria',
        'ngAnimate',
        'ngMaterial',
        'angularVideoBg'



    ]);

    // Execute bootstrapping code and any dependencies.
    app.run(['$rootScope',
        function ($rootScope) {

        }]);
    
    app.config(function($interpolateProvider) {
    	$interpolateProvider.startSymbol('[[');
    	$interpolateProvider.endSymbol(']]');
    	});
    
})();

