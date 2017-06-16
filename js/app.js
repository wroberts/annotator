angular.module('Annotator', [])

  .directive('dashboard', () => {
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
