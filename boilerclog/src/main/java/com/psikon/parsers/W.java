package com.psikon.parsers;

import java.util.List;

import com.psikon.WikiNewsModel;

import info.bliki.wiki.model.IWikiModel;
import info.bliki.wiki.template.AbstractTemplateFunction;
import info.bliki.wiki.template.ITemplateFunction;

/**
 * A custom template function
 * 
 * I've completely forgotten how or why this works, but it's meant to
 * handle cases where the mediawiki syntax looks like this:
 * 
 * {{whatever}}
 * 
 * For some reason gwtwiki was letting this slide and this
 * thing corrects the issue.
 * 
 * @see WikiNewsModel
 */
public class W extends AbstractTemplateFunction {
	
	/**
	 * Singleton I guess
	 */
	public final static ITemplateFunction CONST = new W();

	/**
	 * I really don't remember how this works. Refer to the gwtwiki
	 * documentation.
	 */
	public String parseFunction(List<String> list, IWikiModel model,
			char[] src, int beginIndex, int endIndex, boolean unknown) {
		
		if (list.size() > 1)
		{
			return list.get(1);
		} else if (list.size() == 1) {
			return list.get(0);
		}
		return null;
	}
}
