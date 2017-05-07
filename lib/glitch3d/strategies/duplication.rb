# frozen_string_literal: true
module Glitch3d
  module Duplication
    def alter_vertices(vertices_objects_array)
      iteration_number = 8
      res = []
      iteration_number.times do |_|
        res = copy_random_element(vertices_objects_array, iteration_number, CHUNK_SIZE)
      end
      res
    end

    def alter_faces(faces_objects_array, vertex_objects_array)
      faces_objects_array
    end

    def copy_random_element(collection, iteration_number, chunk_size)
      new_array = collection
      iteration_number.times do 
        rand1 = rand(0..collection.size - 1)
        rand2 = rand(0..collection.size - 1)
        new_array[rand1..rand1 + chunk_size] = new_array[rand2..rand2 + chunk_size]
      end
      new_array
    end
  end
end
