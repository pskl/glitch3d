class Face
  attr_accessor :v1, :v2, :v3

  def initialize(v1, v2, v3)
    @v1 = v1
    @v2 = v2
    @v3 = v3
  end

  def to_s
    "f #{v1} #{v2} #{v3}"
  end

  def fuck(new_reference)
    f = dup
    f.send("#{[:v1, :v2, :v3].sample}=", new_reference)
    f
  end
end
