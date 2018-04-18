// create the module and name it scotchApp
var scotchApp = angular.module('scotchApp', ['ngRoute', 'ngClickCopy'])
	.constant('SECRETAPIURL', 'https://api.reflectiveinc.net/mypass')
	.run(function ($rootScope) {
		$rootScope.secretInfo = {};
		// $rootScope.$on('$routeChangeStart', function (event, next, prev) {
		//  	console.log('route changing...');
		// // 	$('body').addClass('loading');
		// // 	console.log('event: ' + event);
		// // 	console.log('next: ' + next);
		// // 	console.log('prev: ' + prev);
		// });
		// $rootScope.$on('$routeChangeSuccess', function (event, next, prev) {
		//  	console.log('route success');
		// // 	$('body').removeClass('loading');
		// // 	console.log('event: ' + event);
		// // 	console.log('next: ' + next);
		// // 	console.log('prev: ' + prev);
		// });
	})
	.service('spinner', function () {
		return {
			on: function () { $('body').addClass('loading'); },
			off: function () { $('body').removeClass('loading'); }
		}
	})
	.service('apiSecretService', ['$http', '$q', 'SECRETAPIURL', 'spinner', function ($http, $q, url, spinner) {
		return {
			encodeSecret: encodeSecret,
			decodeSecret: decodeSecret
		}
		function encodeSecret(secret, ttl) {
			var deferred = $q.defer();
			data = { secret: secret, ttl: ttl }
			spinner.on();
			$http.put(url, data)
				.success(function(response) {
					console.log(response);
					deferred.resolve(response);
				})
				.error(function(response) {
					console.log(response)
					deferred.reject(response);
				})
				.finally(function(){
					spinner.off();
				});
			return deferred.promise;
		};
		function decodeSecret(key) {
			var deferred = $q.defer();
			var url1 = url + '/' + key;
			spinner.on();
			$http.get(url1)
				.success(function(response) {
					console.log(response);
					deferred.resolve(response);
				})
				.error(function(response) {
					console.log(response);
					deferred.reject(response);
				})
				.finally(function() {
					spinner.off();
				});
			return deferred.promise;
		};
	}])
	.config(function ($routeProvider) {
		$routeProvider
			// route for the home page
			.when('/', {
				templateUrl: 'pages/home.html',
				controller: 'mainController'
			})
			// route for the share page
			.when('/share', {
				templateUrl: 'pages/share.html',
				controller: 'shareController'
			})
			// route for the about page
			.when('/about', {
				templateUrl: 'pages/about.html'
			})
			.when('/:key', {
				templateUrl: 'pages/secret.html',
				controller: 'secretController'
			});
	})
	.controller('mainController', ['$scope', '$rootScope', '$window', 'apiSecretService', function ($scope, $rootScope, $window, secretService) {
		$scope.ttls = [
			{ name: "15 min", value: "900" },
			{ name: "1 Hour", value: "3600" },
			{ name: "1 Day", value: "86400" } //,			{ name: "1 Week", value: "604800" }
		];
		$scope.selectedItem = $scope.ttls[0]; //1 hour default
		$scope.submit = function () {
			if ($scope.password) {
				secretService.encodeSecret($scope.password, $scope.selectedItem.value)
					.then(function(data) {
						console.log('OK: ' + data);
						$rootScope.secretInfo = data;
						$window.location.assign('/#/share');
					})
					.catch(function(error) {
						console.log('ERROR: ' + error);
					});
			}
		};
	}]).controller('shareController', ['$scope', '$rootScope', function ($scope, $rootScope) {
		if ($rootScope.secretInfo.url != null) {
			$scope.message = $rootScope.secretInfo.url;
			$scope.expirey = $rootScope.secretInfo.expires;
		} else {
			$scope.message = "URL not available, please try again"
		}
	}]).controller('secretController', ['$scope', '$routeParams', 'apiSecretService', function ($scope, $routeParams, secretService) {
		secretService.decodeSecret($routeParams.key)
			.then(function(data) {
				$scope.banner = 'Your recovered secret is:';
				$scope.password = data.secret;
			})
			.catch(function(error) {
				$scope.banner = 'The secret has expired or has already been recovered. Please contact the sender of the secret.';
				$('.input-group').hide();
				$('.input-group-button').hide();
			});
	}]);
