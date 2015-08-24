(function(angular) {
  'use strict';

  angular.module('MissionApp',[]);

  function MissionController() {

    var self = this;

var adjectives = Array('Bold','Breaking','Brilliant','Crescent','Dark|Darkness','Desert|Desert','Evening|Darkness','Final','First','July','Last','Libery|Liberty','Magic|Magic','Morning|Morning','Power|Power','Phantom','Present','Roaring|Roar|Scream','Rolling','Sand','Screaming','Soaring','Standing|Stand','Star|Star','Urgent','Utopian','Valiant');
var nouns = Array('Action','Alert','Beauty','Claw','Darkness','Dawn','Day','Desert','Envy','Fall','Fist','Flight','Fury','Guard','Hammer','Hand','Honor','Hope','Hurricane','Liberty','Light','Lightning','Magic','Morning','October','Power','Rain','Repose','Roar','Scream','Skull','Shield','Stand','Star','Storm','Streak','Sun','Thunder','Wind','Wrath');
var colors = Array('Black','Blue','Brown','Gray','Green','Indego','Orange','Purple','Rainbow','Red','Scarlet','Violet','White','Yellow');
var actors = Array('Condor','Eagle','Guardian','Hawk','Hydra','Lady','Lion','Scorpion','Spartan','Titan','Victor','Viking','Warrior');
var mission_grammars = Array(
    {chance:30, grammar: 'adj1 + " " + noun1'},
    {chance:10, grammar: 'color + " " + noun1'},
    {chance:10, grammar: 'color + " " + actor'},
    {chance:10, grammar: 'actor +"\'s " + noun1'},
    {chance:10, grammar: 'noun1 + " of the " + noun2'},
    {chance:10, grammar: 'noun1 + " of " + noun2'},
    {chance:10, grammar: 'noun1 + " of " + color + " " + noun2'},
    {chance:10, grammar: 'adj1 + " " + noun1 + " and " + adj2 + " " + noun2'},
    {chance:3,  grammar: '"Attack of the " + actor + "s"'}
    );
this.getNoun = function(badNouns) {
  return _.chain(nouns)
    .difference(badNouns)
    .sample()
    .value();
};

this.getMissionName = function() {
  var adj1 = _.sample(adjectives);
  var adj2 = _.sample(adjectives);
  while(adj1 == adj2)
    adj2 = _.sample(adjectives);
  var badWords = _.uniq(adj1.split('|').slice(1).concat(adj2.split('|').slice(1)));
  var noun1 = self.getNoun(badWords);
  var noun2 = self.getNoun(badWords);
  while(noun1 == noun2)
    noun2 = self.getNoun(badWords);
  adj1 = adj1.split('|')[0];
  adj2 = adj2.split('|')[0];
  var color = _.sample(colors);
  var actor = _.sample(actors);

  var mission = '';
  var rand = Math.floor(Math.random() * 100 + 1);
  if(rand <= 25)
    mission += 'Operation ';
  else if(rand <= 50)
    mission += 'Project ';
  else if(rand <= 75)
    mission += 'Code: ';

  var sumChance = _.chain(mission_grammars).pluck('chance').reduce(function(sum, c) { return sum + c;}).value();
  rand = Math.floor(Math.random() * sumChance + 1);
  for(var gi in mission_grammars) {
    var g = mission_grammars[gi];
    if(rand > g.chance) {
      rand -= g.chance;
      }
    else {
      mission += eval(g.grammar);
      return mission;
    }
  }
  return '';
};
};

angular.module('MissionApp').controller('MissionController', [MissionController]);
}(window.angular));
