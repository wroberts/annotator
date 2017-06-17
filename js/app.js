import angular from 'angular';
import 'angular-route';

import template from './interface.html';

angular.module('Annotator', ['ngRoute'])

  .directive('dashboard', () => {
    return {
      restrict: 'E',
      transclude: true,
      scope: {},
      controller: ($location) => {
        // todo
        console.log('instantiating annotation interface');
        console.log($location.path());
      },
      template: '<h3>Hello from Angular!</h3>',
      replace: true,
    };
  })

  .config(($locationProvider, $routeProvider) => {
    $locationProvider
      .html5Mode(false)
      .hashPrefix('!');
    $routeProvider
      .when('/:clauseId', {
        restrict: 'E',
        controller: ($scope, $routeParams) => {
          $scope.name = 'AnnotationController';
          $scope.params = $routeParams;
        },
        template,
      });
  });
