// min & max inclusive
function randBetween(min, max) { 
    return Math.floor(Math.random() * (max - min + 1) + min)
}

// interesting
// https://web.archive.org/web/20090717035140if_/javascript.about.com/od/problemsolving/a/modulobug.htm
Number.prototype.mod = function (n) {
    "use strict";
    return ((this % n) + n) % n;
};

Array.prototype.shuffle = function() {
    return this.sort(function() {
        return Math.random() - 0.5;
      });
}
