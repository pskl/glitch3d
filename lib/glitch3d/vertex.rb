class Vertex
  attr_accessor :x, :y, :z, :index

  def initialize(x, y, z, index)
    @x = x
    @y = y
    @z = z
    @index = index
  end

  def to_s
    "v #{x} #{y} #{z}"
  end

  def rand_attr
    [:x, :y, :z].sample
  end

  def fuck
    attr = rand_attr
    send("#{attr}=", send(attr) + Glitch3d.rand_vertex_glitch_offset)
  end

  def max
    [@x.abs, @y.abs].max.round
  end

  def self.furthest(vertices_list)
    furthest_vertices = [
      vertices_list.max_by { |v| v.x },
      vertices_list.max_by { |v| v.y },
      vertices_list.max_by { |v| v.z }
    ]
    max_coord = [
      furthest_vertices[0].x,
      furthest_vertices[1].y,
      furthest_vertices[2].z
    ].max
    furthest_vertices.find { |v| v.x == max_coord || v.y == max_coord || v.z == max_coord }
  end
end
