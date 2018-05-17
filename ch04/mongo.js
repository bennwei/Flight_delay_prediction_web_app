db.on_time_performance.findOne({Carrier: 'DL', FlightDate: '2015-01-01', FlightNum: 478}) // Slow
db.on_time_performance.ensureIndex({Carrier: 1, FlightDate: 1, FlightNum: 1})
db.on_time_performance.findOne({Carrier: 'DL', FlightDate: '2015-01-01', FlightNum: 478}) // Fast

db.on_time_performance.find({Origin: 'ATL', Dest: 'SFO', FlightDate: '2015-01-01'}).sort({DepTime: 1, ArrTime: 1}) // Slow or broken
db.on_time_performance.ensureIndex({Origin: 1, Dest: 1, FlightDate: 1}) // Fast
db.on_time_performance.find({Origin: 'ATL', Dest: 'SFO', FlightDate: '2015-01-01'}).sort({DepTime: 1, ArrTime: 1}) // Fast
