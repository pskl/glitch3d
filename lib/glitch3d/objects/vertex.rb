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

  def self.boundaries(vertices_list)
    [
      vertices_list.max_by(&:x).x.ceil,
      vertices_list.max_by(&:y).y.ceil,
      vertices_list.max_by(&:z).z.ceil
    ]
  end

  # Pass functions like :negative? or :positive?
  def self.subset(x:, y:, z:, vertex_list:)
    vertex_list.select do |vertex|
      vertex.send(x) && vertex.send(y) && vertex.send(z)
    end
  end
end
