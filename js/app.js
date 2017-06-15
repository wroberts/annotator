angular.module('Annotator', [])

  .directive('helloWorld', () => {
    return {
      restrict: 'E',
      transclude: true,
      scope: {},
      controller: () => {
        // todo
      },
      template: '<h3>Hello from Angular!</h3>',
      replace: true,
    };
  });
